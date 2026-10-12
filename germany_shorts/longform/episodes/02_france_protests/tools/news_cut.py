"""Cut a short news/TikTok excerpt and blur every detected face (minors are never shown identifiable).

  python3 tools/news_cut.py SRC START DUR OUT [--no-blur] [--thresh 0.55]

YuNet face detector (tools/yunet.onnx) runs on every frame; boxes are padded, held for a few frames on both sides so a
missed detection does not flash a face, and blurred hard. Audio is dropped (narration runs over it).
"""
import subprocess
import sys
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    a = sys.argv[1:]
    src, start, dur, out = a[0], float(a[1]), float(a[2]), a[3]
    blur = "--no-blur" not in a
    thresh = float(a[a.index("--thresh") + 1]) if "--thresh" in a else 0.55
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                         "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(pr[0]), int(pr[1])
    fps = 30
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", src, "-t", str(dur), "-vf", f"fps={fps}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    frames = [f.copy() for f in np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)]
    h, w = frames[0].shape[:2]
    boxes = [[] for _ in frames]
    if blur:
        s = 960 / max(w, h)
        dw, dh = int(w * s), int(h * s)
        det = cv2.FaceDetectorYN.create(os.path.join(HERE, "yunet.onnx"), "", (dw, dh), thresh, 0.3, 5000)
        for i, f in enumerate(frames):
            _, faces = det.detect(cv2.resize(f, (dw, dh)))
            for r in (faces if faces is not None else []):
                x, y, bw, bh = [v / s for v in r[:4]]
                boxes[i].append((x, y, bw, bh))
    hold = 5
    n_blur = 0
    for i, f in enumerate(frames):
        near = [b for j in range(max(0, i - hold), min(len(frames), i + hold + 1)) for b in boxes[j]]
        for x, y, bw, bh in near:
            cx, cy = x + bw / 2, y + bh / 2
            r = max(bw, bh) * 0.95
            x0, y0, x1, y1 = int(max(cx - r, 0)), int(max(cy - r * 1.15, 0)), int(min(cx + r, w)), int(min(cy + r * 1.05, h))
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            roi = f[y0:y1, x0:x1]
            bw_, bh_ = x1 - x0, y1 - y0
            small = cv2.resize(roi, (max(2, bw_ // 16), max(2, bh_ // 16)), interpolation=cv2.INTER_AREA)
            roi_b = cv2.resize(cv2.resize(small, (max(2, bw_ // 4), max(2, bh_ // 4)), interpolation=cv2.INTER_CUBIC),
                               (bw_, bh_), interpolation=cv2.INTER_LINEAR).astype(np.float32)
            yy, xx = np.mgrid[0:bh_, 0:bw_]
            rr = np.hypot((xx - bw_ / 2) / (bw_ / 2), (yy - bh_ / 2) / (bh_ / 2))
            mask = np.clip((1.0 - rr) / 0.25, 0, 1).astype(np.float32)[..., None]
            f[y0:y1, x0:x1] = (roi * (1 - mask) + roi_b * mask).astype(np.uint8)
            n_blur += 1
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in frames:
        ff.stdin.write(f.tobytes())
    ff.stdin.close()
    ff.wait()
    print(out, f"{len(frames)} frames, {sum(map(len, boxes))} detections, {n_blur} blurred patches")


if __name__ == "__main__":
    main()
