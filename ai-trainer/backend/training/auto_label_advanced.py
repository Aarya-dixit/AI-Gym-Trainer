# auto_label_advanced.py

import cv2
import numpy as np
import os
import sys

# ==============================
# ✅ FIX IMPORT PATH
# ==============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from rep_counter import RepCounter
from mediapipe_compat import mp_pose

# ==============================
# ✅ DATA DIRECTORY
# ==============================
DATA_DIR = os.path.join(BASE_DIR, "training", "data", "videos")


# ==============================
# 🔧 EXTRACT LANDMARKS
# ==============================
def extract_landmarks(results):
    return [
        {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        }
        for lm in results.pose_landmarks.landmark
    ]


# ==============================
# 🎯 AUTO LABEL SINGLE VIDEO
# ==============================
def auto_label_video(video_path, exercise):
    print(f"\n🎯 Processing: {video_path}")

    cap = cv2.VideoCapture(video_path)

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    rep_counter = RepCounter(exercise=exercise)

    phases = []
    errors = []
    scores = []

    phase_map = {
        "top": 0,
        "down": 1,
        "bottom": 2,
        "up": 3
    }

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if not results.pose_landmarks:
            continue

        landmarks = extract_landmarks(results)

        try:
            output = rep_counter.update(landmarks)
        except Exception as e:
            print(f"⚠️ Error in rep_counter: {e}")
            continue

        # ==============================
        # PHASE
        # ==============================
        phase_str = output.get("phase", "top")
        phase = phase_map.get(phase_str, 0)
        phases.append(phase)

        # ==============================
        # ERRORS
        # ==============================
        err = output.get("errors", {})

        errors.append([
            float(err.get("knees_inward", 0)),
            float(err.get("insufficient_depth", 0)),
            float(err.get("back_bending", 0))
        ])

        # ==============================
        # SCORE (simple heuristic)
        # ==============================
        score = 1.0 - sum(errors[-1]) * 0.2
        score = max(0.0, min(1.0, score))
        scores.append(score)

    cap.release()
    pose.close()

    if len(phases) == 0:
        print(f"❌ No valid frames in {video_path}, skipping...")
        return

    # ==============================
    # SAVE LABELS
    # ==============================
    labels = {
        "phase": np.array(phases),
        "errors": np.array(errors),
        "score": np.array(scores)
    }

    save_path = video_path.replace(".mp4", "_labels.npy")
    np.save(save_path, labels)

    print(f"✅ Saved labels: {save_path}")
    print(f"   Frames processed: {frame_count}")
    print(f"   Valid frames: {len(phases)}")


# ==============================
# 🔁 RUN FOR ALL VIDEOS
# ==============================
def run_auto_label():
    if not os.path.exists(DATA_DIR):
        print(f"❌ DATA_DIR not found: {DATA_DIR}")
        return

    files = os.listdir(DATA_DIR)

    print(f"\n📂 Found {len(files)} files in dataset\n")

    for file in files:
        if not file.endswith(".mp4"):
            continue

        video_path = os.path.join(DATA_DIR, file)

        # Detect exercise from filename
        if "squat" in file:
            exercise = "squat"
        elif "boxing" in file:
            exercise = "boxing"
        elif "jumping" in file:
            exercise = "jumping"
        elif "waving" in file:
            exercise = "waving"
        else:
            print(f"⚠️ Skipping unknown exercise: {file}")
            continue

        auto_label_video(video_path, exercise)


# ==============================
# 🚀 MAIN
# ==============================
if __name__ == "__main__":
    print("🚀 Starting Auto Labeling Pipeline...")
    run_auto_label()
    print("\n✅ All videos processed!")