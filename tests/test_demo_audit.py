import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DemoAuditTests(unittest.TestCase):
    def test_demo_audit_matches_video(self):
        video = ROOT / "outputs" / "demo.mp4"
        audit = json.loads((ROOT / "artifacts" / "demo-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["artifact"], "outputs/demo.mp4")
        self.assertEqual(audit["slide_count"], 6)
        self.assertEqual(audit["stream_types"], ["audio", "video"])
        self.assertEqual(audit["failure_count"], 0)
        self.assertGreaterEqual(audit["duration_seconds"], 90)
        self.assertLessEqual(audit["duration_seconds"], 180)
        self.assertEqual(audit["sha256"], hashlib.sha256(video.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
