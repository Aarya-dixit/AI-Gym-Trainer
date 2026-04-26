# AI Gym Trainer

Real-time posture correction and exercise analysis system using computer vision and deep learning.
Built with MediaPipe and a Transformer-based model for form evaluation and feedback.

---

## Overview

An end-to-end system that tracks human movement, analyzes exercise form, and provides real-time feedback. It combines pose estimation, feature engineering, and temporal modeling to evaluate workout performance.

---

## Features

* Real-time pose detection (33 landmarks)
* Transformer-based temporal analysis
* Automatic repetition counting
* Exercise phase and error detection
* Instant feedback on form
* Runs locally with low latency

---

## Supported Exercises

Squats · Boxing · Waving · Jumping Jacks

---

## Tech Stack

**Frontend**
React · TypeScript · TailwindCSS · MediaPipe

**Backend**
FastAPI · PyTorch · WebSockets

**Core**
Computer Vision · Transformer Model · Feature Engineering

---

## Workflow

1. Capture webcam input
2. Extract pose landmarks
3. Generate feature vectors
4. Process sequences via Transformer
5. Detect phases and errors
6. Provide feedback and count reps

---

## Structure

```
ai-trainer/
├── backend/
├── frontend-react/
├── models/
└── training/
```

---

## Setup

### Backend

```
cd ai-trainer/backend
python -m venv myenv
source myenv/bin/activate   # Windows: myenv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend

```
cd ai-trainer/frontend-react
npm install
npm run dev
```

---

## Performance

* ~30 FPS real-time processing
* <50 ms latency per frame
* Lightweight model (~2 MB)

---

## Contributors

Kanishka Gole — https://github.com/KanishkaGole
Arya Dixit — https://github.com/Aarya-dixit

---

## License

MIT License
