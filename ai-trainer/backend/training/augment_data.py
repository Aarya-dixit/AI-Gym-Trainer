# augment_data.py

import cv2
import os

# ✅ TARGET DIRECTORY
DATA_DIR = "data/videos"

def augment_video(video_path):
    cap = cv2.VideoCapture(video_path)

    # ✅ Auto resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30

    filename = os.path.basename(video_path).replace(".mp4", "")

    augmentations = [
        ('original', lambda x: x),
        ('flip', lambda x: cv2.flip(x, 1)),
        ('bright', lambda x: cv2.convertScaleAbs(x, alpha=1.2, beta=10)),
        ('dark', lambda x: cv2.convertScaleAbs(x, alpha=0.8, beta=-10)),
        ('zoom', lambda x: safe_zoom(x))
    ]

    for name, aug_func in augmentations:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        output_path = os.path.join(DATA_DIR, f"{filename}_{name}.mp4")

        out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            augmented = aug_func(frame)

            # Ensure size consistency
            augmented = cv2.resize(augmented, (width, height))

            out.write(augmented)

        out.release()
        print(f"✅ Saved: {output_path}")

    cap.release()


# ✅ SAFE ZOOM FUNCTION
def safe_zoom(frame):
    h, w = frame.shape[:2]

    crop = 50
    if h > 2 * crop and w > 2 * crop:
        zoomed = frame[crop:-crop, crop:-crop]
        return zoomed
    return frame


# 🔥 RUN AUGMENTATION

exercises = ["squat", "boxing", "jumping", "waving"]

for exercise in exercises:
    for i in range(3):
        video_path = os.path.join(DATA_DIR, f"{exercise}_{i+1}.mp4")

        if os.path.exists(video_path):
            augment_video(video_path)
        else:
            print(f"⚠️ Skipping missing file: {video_path}")