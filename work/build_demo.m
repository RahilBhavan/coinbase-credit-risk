#import <AVFoundation/AVFoundation.h>
#import <CoreGraphics/CoreGraphics.h>
#import <CoreVideo/CoreVideo.h>
#import <Foundation/Foundation.h>
#import <ImageIO/ImageIO.h>

static void Die(NSString *message) {
    fprintf(stderr, "%s\n", message.UTF8String);
    exit(1);
}

static CGImageRef LoadImage(NSString *path) {
    NSURL *url = [NSURL fileURLWithPath:path];
    CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)url, NULL);
    if (!source) Die([NSString stringWithFormat:@"Cannot load %@", path]);
    CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
    CFRelease(source);
    if (!image) Die([NSString stringWithFormat:@"Cannot decode %@", path]);
    return image;
}

static CVPixelBufferRef MakeFrame(CGImageRef image) {
    NSDictionary *attrs = @{
        (__bridge NSString *)kCVPixelBufferCGImageCompatibilityKey: @YES,
        (__bridge NSString *)kCVPixelBufferCGBitmapContextCompatibilityKey: @YES,
    };
    CVPixelBufferRef buffer = NULL;
    CVReturn status = CVPixelBufferCreate(kCFAllocatorDefault, 1920, 1080,
        kCVPixelFormatType_32ARGB, (__bridge CFDictionaryRef)attrs, &buffer);
    if (status != kCVReturnSuccess || !buffer) Die(@"Cannot allocate video frame");
    CVPixelBufferLockBaseAddress(buffer, 0);
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(CVPixelBufferGetBaseAddress(buffer),
        1920, 1080, 8, CVPixelBufferGetBytesPerRow(buffer),
        colorSpace, (CGBitmapInfo)kCGImageAlphaNoneSkipFirst);
    CGColorSpaceRelease(colorSpace);
    if (!context) Die(@"Cannot create frame context");
    CGContextTranslateCTM(context, 0, 1080);
    CGContextScaleCTM(context, 1, -1);
    CGContextSetInterpolationQuality(context, kCGInterpolationHigh);
    CGContextDrawImage(context, CGRectMake(0, 0, 1920, 1080), image);
    CGContextRelease(context);
    CVPixelBufferUnlockBaseAddress(buffer, 0);
    return buffer;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc < 4) Die(@"Usage: build_demo output.mp4 seconds-per-slide slide.png [...]");
        NSString *outputPath = [NSString stringWithUTF8String:argv[1]];
        double seconds = atof(argv[2]);
        if (seconds <= 0) Die(@"Slide duration must be positive");
        [[NSFileManager defaultManager] removeItemAtPath:outputPath error:nil];

        NSError *error = nil;
        AVAssetWriter *writer = [[AVAssetWriter alloc]
            initWithURL:[NSURL fileURLWithPath:outputPath]
            fileType:AVFileTypeQuickTimeMovie error:&error];
        if (!writer) Die(error.localizedDescription);
        NSDictionary *settings = @{
            AVVideoCodecKey: AVVideoCodecTypeJPEG,
            AVVideoWidthKey: @1920,
            AVVideoHeightKey: @1080,
            AVVideoCompressionPropertiesKey: @{ AVVideoQualityKey: @0.88 },
        };
        AVAssetWriterInput *input = [AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo outputSettings:settings];
        input.expectsMediaDataInRealTime = NO;
        AVAssetWriterInputPixelBufferAdaptor *adaptor =
            [AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:input
                sourcePixelBufferAttributes:@{
                    (__bridge NSString *)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_32ARGB),
                    (__bridge NSString *)kCVPixelBufferWidthKey: @1920,
                    (__bridge NSString *)kCVPixelBufferHeightKey: @1080,
                }];
        if (![writer canAddInput:input]) Die(@"Cannot add video input");
        [writer addInput:input];
        if (![writer startWriting]) Die(writer.error.localizedDescription);
        [writer startSessionAtSourceTime:kCMTimeZero];

        int64_t frame = 0;
        int framesPerSlide = (int)llround(seconds * 2.0);
        for (int i = 3; i < argc; i++) {
            CGImageRef image = LoadImage([NSString stringWithUTF8String:argv[i]]);
            CVPixelBufferRef pixel = MakeFrame(image);
            CGImageRelease(image);
            for (int j = 0; j < framesPerSlide; j++, frame++) {
                while (!input.readyForMoreMediaData) [NSThread sleepForTimeInterval:0.01];
                if (![adaptor appendPixelBuffer:pixel withPresentationTime:CMTimeMake(frame, 2)]) {
                    Die(writer.error.localizedDescription ?: @"Cannot append frame");
                }
            }
            CVPixelBufferRelease(pixel);
        }
        [input markAsFinished];
        dispatch_semaphore_t done = dispatch_semaphore_create(0);
        [writer finishWritingWithCompletionHandler:^{ dispatch_semaphore_signal(done); }];
        dispatch_semaphore_wait(done, DISPATCH_TIME_FOREVER);
        if (writer.status != AVAssetWriterStatusCompleted) Die(writer.error.localizedDescription ?: @"Video writing failed");
        printf("%s\n", outputPath.UTF8String);
    }
    return 0;
}
