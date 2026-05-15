import argparse
import time
from pathlib import Path


try:
    import cv2
except Exception:
    cv2 = None


CLASS_ALIASES = {
    "1": "oily",
    "2": "dry",
    "3": "normal",
    "4": "acne",
}


def ensure_opencv():
    if cv2 is None:
        raise RuntimeError(
            "OpenCV is required for webcam capture. Install it with `pip install opencv-python`."
        )


def build_output_path(root, split, label, subject, index):
    directory = Path(root) / split / label
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return directory / f"{subject}_{timestamp}_{index:03d}.jpg"


def draw_overlay(frame, label, split, subject, saved_count):
    instructions = [
        f"Label: {label} | Split: {split} | Subject: {subject}",
        "Press SPACE to save frame",
        "Press 1=oily  2=dry  3=normal  4=acne",
        "Press T/V/E for train/val/test, Q to quit",
        f"Saved this session: {saved_count}",
    ]
    y = 30
    for line in instructions:
        cv2.putText(frame, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 255, 120), 2)
        y += 30

    height, width = frame.shape[:2]
    x1, y1 = int(width * 0.20), int(height * 0.12)
    x2, y2 = int(width * 0.80), int(height * 0.88)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 180), 2)


def crop_face_like_region(frame):
    height, width = frame.shape[:2]
    x1, y1 = int(width * 0.20), int(height * 0.12)
    x2, y2 = int(width * 0.80), int(height * 0.88)
    return frame[y1:y2, x1:x2]


def collect(root, subject, camera_index=0):
    ensure_opencv()
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError("Could not open webcam.")

    current_label = "normal"
    current_split = "train"
    saved_count = 0
    image_index = 1

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("Failed to read a frame from the webcam.")

            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()
            draw_overlay(display_frame, current_label, current_split, subject, saved_count)
            cv2.imshow("DermaAura Webcam Dataset Collector", display_frame)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                break
            if chr(key) in CLASS_ALIASES:
                current_label = CLASS_ALIASES[chr(key)]
            elif key in (ord("t"), ord("T")):
                current_split = "train"
            elif key in (ord("v"), ord("V")):
                current_split = "val"
            elif key in (ord("e"), ord("E")):
                current_split = "test"
            elif key == 32:
                cropped = crop_face_like_region(frame)
                output_path = build_output_path(root, current_split, current_label, subject, image_index)
                cv2.imwrite(str(output_path), cropped)
                print(f"saved {output_path}")
                image_index += 1
                saved_count += 1
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Capture webcam images for the DermaAura skin dataset.")
    parser.add_argument("--root", default="data/skin_types", help="Dataset root directory")
    parser.add_argument("--subject", required=True, help="Short subject identifier, e.g. person01")
    parser.add_argument("--camera-index", type=int, default=0, help="OpenCV camera index")
    args = parser.parse_args()

    collect(root=args.root, subject=args.subject, camera_index=args.camera_index)


if __name__ == "__main__":
    main()
