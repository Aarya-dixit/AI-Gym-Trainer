# quick_record.py

import cv2
import time
import os

# ✅ TARGET DIRECTORY
SAVE_DIR = "data/videos"

# Create folder if not exists
os.makedirs(SAVE_DIR, exist_ok=True)


def record_exercise(exercise_name, duration):
    cap = cv2.VideoCapture(0)

    # ✅ Correct FPS
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # ✅ Full path
    filepath = os.path.join(SAVE_DIR, f"{exercise_name}.mp4")

    out = cv2.VideoWriter(filepath, fourcc, fps, (640, 480))

    print(f"\n🔥🔥🔥🔥🔥🔥🔥🔥🔥\n Recording {exercise_name} for {duration} seconds...")
    print("3... 2... 1... GO!\n🔥🔥🔥🔥🔥🔥🔥🔥🔥\n")
    time.sleep(3)

    start = time.time()

    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"✅ Saved: {filepath} \n ⚙️ ⚙️ ⚙️ ⚙️ ⚙️\nNext video recording begins in 3 seconds!!\n ⚙️ ⚙️ ⚙️ ⚙️ ⚙️\n")


# 🔥 RECORD DATASET

exercises = ["squat", "boxing", "jumping", "waving"]
dur =10
for exercise in exercises:
    for i in range(3):
        record_exercise(f"{exercise}_{i+1}", duration=dur)
        time.sleep(3)