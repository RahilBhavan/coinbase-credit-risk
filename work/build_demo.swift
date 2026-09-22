import AVFoundation
import CoreGraphics
import Foundation
import ImageIO

struct Segment {
    let imageURL: URL
    let audioURL: URL
    let duration: CMTime
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}

func loadImage(_ url: URL) -> CGImage {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        fail("Cannot load slide image: \(url.path)")
    }
    return image
}

func audioDuration(_ url: URL) -> CMTime {
    let asset = AVURLAsset(url: url)
    let seconds = asset.duration.seconds
    guard seconds.isFinite && seconds > 0 else { fail("Invalid audio duration: \(url.path)") }
    return CMTime(seconds: seconds + 0.35, preferredTimescale: 600)
}

func makePixelBuffer(_ image: CGImage, width: Int, height: Int) -> CVPixelBuffer {
    var buffer: CVPixelBuffer?
    let attrs: [CFString: Any] = [
        kCVPixelBufferCGImageCompatibilityKey: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey: true,
    ]
    let status = CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, attrs as CFDictionary, &buffer)
    guard status == kCVReturnSuccess, let pixelBuffer = buffer else { fail("Cannot create pixel buffer") }
    CVPixelBufferLockBaseAddress(pixelBuffer, [])
    defer { CVPixelBufferUnlockBaseAddress(pixelBuffer, []) }
    guard let context = CGContext(
        data: CVPixelBufferGetBaseAddress(pixelBuffer), width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
    ) else { fail("Cannot create drawing context") }
    context.setFillColor(CGColor(gray: 0.96, alpha: 1))
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    context.translateBy(x: 0, y: CGFloat(height))
    context.scaleBy(x: 1, y: -1)
    context.interpolationQuality = .high
    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    return pixelBuffer
}

func buildVideo(segments: [Segment], output: URL) throws -> [CMTime] {
    try? FileManager.default.removeItem(at: output)
    let writer = try AVAssetWriter(outputURL: output, fileType: .mov)
    let settings: [String: Any] = [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: 1920,
        AVVideoHeightKey: 1080,
        AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 5_000_000],
    ]
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
    input.expectsMediaDataInRealTime = false
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(
        assetWriterInput: input,
        sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
            kCVPixelBufferWidthKey as String: 1920,
            kCVPixelBufferHeightKey as String: 1080,
        ]
    )
    guard writer.canAdd(input) else { fail("Cannot add video input") }
    writer.add(input)
    guard writer.startWriting() else { fail("Cannot start video writer: \(writer.error?.localizedDescription ?? "unknown")") }
    writer.startSession(atSourceTime: .zero)
    var starts: [CMTime] = []
    var cursor = CMTime.zero
    let frameStep = CMTime(value: 1, timescale: 2)
    for segment in segments {
        starts.append(cursor)
        let pixel = makePixelBuffer(loadImage(segment.imageURL), width: 1920, height: 1080)
        let end = cursor + segment.duration
        var frameTime = cursor
        while frameTime < end {
            while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.01) }
            guard adaptor.append(pixel, withPresentationTime: frameTime) else {
                fail("Cannot append frame: \(writer.error?.localizedDescription ?? "unknown")")
            }
            frameTime = frameTime + frameStep
        }
        cursor = end
    }
    input.markAsFinished()
    let semaphore = DispatchSemaphore(value: 0)
    writer.finishWriting { semaphore.signal() }
    semaphore.wait()
    guard writer.status == .completed else { fail("Video writing failed: \(writer.error?.localizedDescription ?? "unknown")") }
    return starts
}

func combine(videoURL: URL, segments: [Segment], starts: [CMTime], output: URL) throws {
    try? FileManager.default.removeItem(at: output)
    let composition = AVMutableComposition()
    let videoAsset = AVURLAsset(url: videoURL)
    guard let sourceVideo = videoAsset.tracks(withMediaType: .video).first,
          let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid) else {
        fail("Cannot read generated video")
    }
    try videoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: videoAsset.duration), of: sourceVideo, at: .zero)
    for (index, segment) in segments.enumerated() {
        let audioAsset = AVURLAsset(url: segment.audioURL)
        guard let sourceAudio = audioAsset.tracks(withMediaType: .audio).first,
              let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
            fail("Cannot read narration: \(segment.audioURL.path)")
        }
        let usable = min(audioAsset.duration, segment.duration)
        try audioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: usable), of: sourceAudio, at: starts[index])
    }
    guard let export = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
        fail("Cannot create export session")
    }
    export.outputURL = output
    export.outputFileType = .mp4
    export.shouldOptimizeForNetworkUse = true
    let semaphore = DispatchSemaphore(value: 0)
    export.exportAsynchronously { semaphore.signal() }
    semaphore.wait()
    guard export.status == .completed else { fail("Export failed: \(export.error?.localizedDescription ?? "unknown")") }
}

let args = CommandLine.arguments
guard args.count >= 5, (args.count - 3) % 2 == 0 else {
    fail("Usage: build_demo temp.mov output.mp4 slide.png narration.aiff [slide.png narration.aiff ...]")
}
let temporary = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2])
var segments: [Segment] = []
var index = 3
while index < args.count {
    let image = URL(fileURLWithPath: args[index])
    let audio = URL(fileURLWithPath: args[index + 1])
    segments.append(Segment(imageURL: image, audioURL: audio, duration: audioDuration(audio)))
    index += 2
}
let starts = try buildVideo(segments: segments, output: temporary)
try combine(videoURL: temporary, segments: segments, starts: starts, output: output)
try? FileManager.default.removeItem(at: temporary)
print(output.path)
