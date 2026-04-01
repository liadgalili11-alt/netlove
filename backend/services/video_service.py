"""
Video frame extraction service.

GPT-4o does not accept raw MP4 input, so we extract representative
frames and send them as multi-image messages. We sample up to MAX_FRAMES
evenly spaced frames across the video duration.

How it works:
1. cv2.VideoCapture opens the MP4 file from disk.
2. We calculate evenly spaced frame indices.
3. Each frame is JPEG-encoded to bytes and returned.
"""

import cv2

MAX_FRAMES = 8


def extract_frames(file_path: str) -> list[bytes]:
    cap = cv2.VideoCapture(file_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return []

    count = min(MAX_FRAMES, total)
    indices = [int(i * (total - 1) / max(count - 1, 1)) for i in range(count)]

    frames: list[bytes] = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ok:
            frames.append(buf.tobytes())

    cap.release()
    return frames
