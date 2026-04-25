# System Architecture Documentation

Complete technical documentation of the AI Personal Gym Trainer system.

## Table of Contents
1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Module Specifications](#module-specifications)
4. [Model Architecture](#model-architecture)
5. [Feature Engineering](#feature-engineering)
6. [Training Pipeline](#training-pipeline)
7. [Real-time Inference](#real-time-inference)
8. [API Specification](#api-specification)

---

## System Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                              │
│  ┌────────────┐    ┌──────────────┐    ┌─────────────┐      │
│  │  Webcam    │───▶│  MediaPipe   │───▶│  WebSocket  │      │
│  │  Capture   │    │  Pose (33)   │    │   Client    │      │
│  └────────────┘    └──────────────┘    └──────┬──────┘      │
│                                                 │              │
└─────────────────────────────────────────────────┼─────────────┘
                                                  │
                                        WebSocket │ JSON
                                                  │
┌─────────────────────────────────────────────────▼─────────────┐
│                         BACKEND                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              INFERENCE PIPELINE                       │    │
│  │                                                        │    │
│  │  ┌─────────────────┐                                 │    │
│  │  │ Feature         │  Extracts 175 features          │    │
│  │  │ Extractor       │  (angles, vectors, velocity)    │    │
│  │  └────────┬────────┘                                 │    │
│  │           │                                           │    │
│  │  ┌────────▼────────┐                                 │    │
│  │  │ Sliding Window  │  Buffers 30 frames              │    │
│  │  │ Buffer (FIFO)   │  Shape: (30, 175)               │    │
│  │  └────────┬────────┘                                 │    │
│  │           │                                           │    │
│  │  ┌────────▼────────┐                                 │    │
│  │  │ Transformer     │  Temporal analysis              │    │
│  │  │ Model           │  Outputs: phase, errors, score  │    │
│  │  └────────┬────────┘                                 │    │
│  │           │                                           │    │
│  │  ┌────────▼────────┐                                 │    │
│  │  │ Rep Counter     │  State machine                  │    │
│  │  │ (State Machine) │  Counts repetitions             │    │
│  │  └────────┬────────┘                                 │    │
│  │           │                                           │    │
│  │  ┌────────▼────────┐                                 │    │
│  │  │ Feedback        │  Maps errors to messages        │    │
│  │  │ Engine          │  Throttles output               │    │
│  │  └────────┬────────┘                                 │    │
│  │           │                                           │    │
│  └───────────┼───────────────────────────────────────────┘    │
│              │                                                 │
│  ┌───────────▼───────────┐                                    │
│  │  WebSocket Response   │                                    │
│  │  {rep, phase, score,  │                                    │
│  │   feedback, errors}   │                                    │
│  └───────────────────────┘                                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Frame Processing Pipeline

```
1. CAPTURE (Frontend)
   └─▶ Webcam frame (1280x720 RGB)

2. POSE DETECTION (Frontend - MediaPipe)
   └─▶ 33 landmarks × (x, y, z, visibility)

3. TRANSMISSION (WebSocket)
   └─▶ JSON: {"landmarks": [...]}

4. FEATURE EXTRACTION (Backend)
   └─▶ 175-dimensional feature vector
       ├─ 7 joint angles
       ├─ 36 bone vectors (12 bones × 3D)
       ├─ 99 velocity features (33 × 3D)
       └─ 33 visibility scores

5. BUFFERING (Backend)
   └─▶ Sliding window: (30, 175)

6. MODEL INFERENCE (Backend)
   └─▶ Outputs:
       ├─ Phase logits: (4,)
       ├─ Error logits: (3,)
       └─ Score: (1,)

7. POST-PROCESSING (Backend)
   └─▶ Rep counting + Feedback generation

8. RESPONSE (WebSocket)
   └─▶ JSON: {rep_count, phase, score, feedback, errors}

9. VISUALIZATION (Frontend)
   └─▶ Update UI + Draw skeleton
```

---

## Module Specifications

### 1. Feature Extractor (`feature_extractor.py`)

**Purpose:** Convert raw pose landmarks into meaningful skeletal features

**Input:**
- 33 MediaPipe landmarks
- Each landmark: `{x, y, z, visibility}`

**Processing:**
1. **Normalization**
   - Center at hip midpoint
   - Scale by torso length
   - Makes pose translation/scale invariant

2. **Angle Computation**
   - Left/right knee angles
   - Left/right elbow angles
   - Left/right hip angles
   - Torso angle (back straightness)

3. **Bone Vectors**
   - 12 key bone connections
   - 3D vectors (x, y, z)
   - Captures limb orientations

4. **Velocity**
   - Frame-to-frame difference
   - 33 landmarks × 3D = 99 features
   - Captures motion dynamics

5. **Visibility**
   - Confidence scores
   - Used for handling occlusions

**Output:** 175-dimensional feature vector

**Key Methods:**
- `extract(landmarks)`: Main extraction function
- `_normalize_pose(coords)`: Normalization
- `_compute_angles(coords)`: Joint angles
- `_compute_bone_vectors(coords)`: Bone vectors
- `_compute_velocity(current, previous)`: Velocity

---

### 2. Model (`model.py`)

**Architecture:** Temporal Transformer Encoder

```
Input: (batch, seq_len=30, features=175)
  │
  ├─▶ Linear Projection: 175 → 128
  │
  ├─▶ Positional Encoding (sinusoidal)
  │
  ├─▶ Transformer Encoder × 3 layers
  │   ├─ Multi-head attention (4 heads)
  │   ├─ Feed-forward (256 dim)
  │   └─ Layer norm + residual
  │
  ├─▶ Global Average Pooling (time dimension)
  │
  └─▶ Three Output Heads:
      ├─▶ Phase Head: 128 → 64 → 4 (softmax)
      ├─▶ Error Head: 128 → 64 → 3 (sigmoid)
      └─▶ Score Head: 128 → 64 → 1 (sigmoid)

Output: (phase_logits, error_logits, score)
```

**Parameters:**
- Total: ~500K parameters
- d_model: 128
- n_heads: 4
- n_layers: 3
- feedforward_dim: 256

**Loss Function:**
```python
L_total = L_phase + L_error + L_score
        = CrossEntropy(phase) + BCE(errors) + MSE(score)
```

---

### 3. Rep Counter (`rep_counter.py`)

**Purpose:** Deterministic state machine for counting repetitions across multiple exercises

**Supported Exercises:**

1. **Squat:**
```
TOP → DOWN → BOTTOM → UP → TOP
```
- Rep completes on `BOTTOM → UP` transition
- Detects hip-knee distance

2. **Boxing:**
```
RETRACTED → EXTENDED → RETRACTED
```
- Rep completes on hand extension
- Detects hand distance from shoulder

3. **Waving:**
```
DOWN → UP → DOWN
```
- Rep completes on hand raise
- Detects hand above shoulder

4. **Jumping:**
```
COMPRESSED → EXTENDED → COMPRESSED
```
- Rep completes on landing
- Detects leg compression/extension

**Smoothing:**
- Uses 3-frame sliding window
- Takes majority vote
- Prevents false transitions

**Rep Completion:**
- Exercise-specific transition detection
- Ensures full range of motion
- Prevents partial rep counting

---

### 4. Feedback Engine (`feedback.py`)

**Purpose:** Generate exercise-specific coaching feedback

**Features:**
- Exercise-specific encouragement messages
- Error detection and prioritization
- Real-time coaching feedback
- Throttled message delivery

**Encouragement Messages by Exercise:**

1. **Squat:**
   - "Great form! Keep it up!"
   - "Excellent depth!"
   - "Perfect control!"

2. **Boxing:**
   - "Powerful punch!"
   - "Great speed!"
   - "Excellent form!"

3. **Waving:**
   - "Smooth motion!"
   - "Great rhythm!"
   - "Perfect wave!"

4. **Jumping:**
   - "Great height!"
   - "Explosive power!"
   - "Perfect landing!"

**Error Types:**
1. **Knees Inward** (Priority: 2)
   - Message: "Keep knees aligned with toes"
   
2. **Insufficient Depth** (Priority: 1)
   - Message: "Go lower"
   
3. **Back Bending** (Priority: 3)
   - Message: "Keep your back straight"

**Logic:**
1. Check error probabilities against threshold (0.5)
2. If no errors: provide encouragement
3. If errors: sort by priority
4. Display highest priority error
5. Optionally show secondary error
6. Throttle messages (2-second minimum)

**Throttling:**
- Prevents feedback spam
- Maintains last message during throttle period
- Improves user experience

---

### 5. Inference Pipeline (`inference.py`)

**Purpose:** Orchestrate complete inference flow

**Components:**
- Feature Extractor
- Sliding Window Buffer (deque, maxlen=30)
- Transformer Model
- Rep Counter
- Feedback Engine

**Process:**
1. Receive landmarks
2. Extract features
3. Add to buffer
4. Wait until buffer full (30 frames)
5. Run model inference
6. Update rep counter
7. Generate feedback
8. Return results

**State Management:**
- Maintains buffer state
- Tracks previous frames
- Handles reset

---

## Feature Engineering

### Feature Vector Breakdown (175 dimensions)

```
┌─────────────────────────────────────────────┐
│ FEATURE GROUP          │ DIM  │ DESCRIPTION │
├────────────────────────┼──────┼─────────────┤
│ Joint Angles           │  7   │ Key angles  │
│  ├─ Left knee          │  1   │             │
│  ├─ Right knee         │  1   │             │
│  ├─ Left elbow         │  1   │             │
│  ├─ Right elbow        │  1   │             │
│  ├─ Left hip           │  1   │             │
│  ├─ Right hip          │  1   │             │
│  └─ Back/torso         │  1   │             │
├────────────────────────┼──────┼─────────────┤
│ Bone Vectors           │ 36   │ 12 × 3D     │
│  ├─ Arms (4 bones)     │ 12   │             │
│  ├─ Legs (4 bones)     │ 12   │             │
│  └─ Torso (4 bones)    │ 12   │             │
├────────────────────────┼──────┼─────────────┤
│ Velocity               │ 99   │ 33 × 3D     │
│  └─ Frame difference   │      │             │
├────────────────────────┼──────┼─────────────┤
│ Visibility             │ 33   │ Confidence  │
├────────────────────────┼──────┼─────────────┤
│ TOTAL                  │ 175  │             │
└─────────────────────────────────────────────┘
```

### Why These Features?

1. **Angles:** Capture joint flexion/extension
2. **Vectors:** Capture limb orientations in 3D space
3. **Velocity:** Capture motion dynamics and speed
4. **Visibility:** Handle occlusions and low confidence

---

## Training Pipeline

### Dataset Format

```
data/processed/
├── sequences.npy        # (N, 30, 175) - Input sequences
├── phase_labels.npy     # (N,) - Phase labels (0-3)
├── error_labels.npy     # (N, 3) - Binary error flags
└── score_labels.npy     # (N,) - Form scores (0-1)
```

### Training Configuration

```python
BATCH_SIZE = 32
NUM_EPOCHS = 30
LEARNING_RATE = 1e-3
OPTIMIZER = Adam
VAL_SPLIT = 0.2
SEQUENCE_LENGTH = 30
STRIDE = 15  # For sliding window
```

### Training Loop

```python
for epoch in range(NUM_EPOCHS):
    # Training
    for batch in train_loader:
        phase_logits, error_logits, score = model(sequences)
        
        loss_phase = CrossEntropy(phase_logits, phase_labels)
        loss_error = BCE(error_logits, error_labels)
        loss_score = MSE(score, score_labels)
        
        loss = loss_phase + loss_error + loss_score
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    # Validation
    val_loss = validate(model, val_loader)
    
    # Save best model
    if val_loss < best_loss:
        save_checkpoint(model, path)
```

---

## Real-time Inference

### Performance Characteristics

- **Latency:** <50ms per frame (CPU)
- **Throughput:** 30+ FPS
- **Memory:** ~500MB RAM
- **Model Size:** ~2MB

### Optimization Strategies

1. **Sliding Window:** Only process when buffer full
2. **Model Efficiency:** Small transformer (128 dim)
3. **Feature Caching:** Reuse previous frame data
4. **Batch Size 1:** Single-sample inference
5. **CPU Inference:** No GPU required

### Bottlenecks

1. **MediaPipe:** ~20ms (frontend)
2. **Feature Extraction:** ~5ms
3. **Model Inference:** ~15ms
4. **Post-processing:** ~5ms
5. **Network:** ~5ms

**Total:** ~50ms → 20 FPS achievable

---

## API Specification

### WebSocket Endpoint: `/ws/live`

**Connection:**
```javascript
ws = new WebSocket('ws://localhost:8000/ws/live');
```

**Input Message:**
```json
{
  "landmarks": [
    {"x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.95},
    ...  // 33 landmarks total
  ]
}
```

**Output Message (Buffering):**
```json
{
  "status": "buffering",
  "message": "Collecting frames..."
}
```

**Output Message (Ready):**
```json
{
  "rep_count": 5,
  "phase": "bottom",
  "score": 0.87,
  "feedback": "Good form!",
  "errors": {
    "knees_inward": 0.12,
    "insufficient_depth": 0.05,
    "back_bending": 0.08
  }
}
```

**Error Message:**
```json
{
  "error": "Expected 33 landmarks, got 32"
}
```

### REST Endpoints

**Health Check:**
```
GET /health
Response: {"status": "healthy", "model_loaded": true}
```

**Reset Session:**
```
POST /reset
Response: {"status": "reset"}
```

---

## Extension Points

### Adding New Exercises

1. **Add Detection Logic:** Create `_count_exercise()` method in `rep_counter.py`
   ```python
   def _count_pushup(self, landmarks: list) -> dict:
       # Implement pushup-specific logic
       # Detect shoulder height, arm extension, etc.
       pass
   ```

2. **Add Instructions:** Update `app.js` instructions object
   ```javascript
   pushup: `<strong>Push-up:</strong>
       <ul>
           <li>Start in plank position</li>
           <li>Lower body until chest near ground</li>
           <li>Push back up to starting position</li>
       </ul>`
   ```

3. **Add UI Option:** Update HTML select element
   ```html
   <option value="pushup">💪 Push-up</option>
   ```

4. **Add Feedback:** Update `feedback.py` encouragement messages
   ```python
   'pushup': [
       "Great form!",
       "Excellent strength!",
       "Perfect control!"
   ]
   ```

5. **Test:** Run the application and test with your movements

### Current Exercise Implementation

All 4 exercises (Squat, Boxing, Waving, Jumping) are fully implemented with:
- ✅ Rule-based rep counting
- ✅ Exercise-specific instructions
- ✅ Real-time feedback
- ✅ Phase detection
- ✅ No training required

### Multi-Exercise Support

The system already supports multiple exercises with:
- Exercise selection dropdown
- Dynamic instruction updates
- Exercise-specific feedback
- Automatic rep counter switching
- Real-time UI synchronization

### Mobile Deployment

1. **Model Quantization:** Reduce to INT8
2. **ONNX Export:** Convert PyTorch → ONNX
3. **TensorFlow Lite:** For mobile inference
4. **Edge TPU:** For hardware acceleration

---

## Performance Metrics

### Model Metrics

- **Phase Accuracy:** Target >90%
- **Error Detection F1:** Target >0.85
- **Score MAE:** Target <0.1

### System Metrics

- **End-to-end Latency:** <100ms
- **Frame Rate:** >20 FPS
- **Memory Usage:** <1GB
- **CPU Usage:** <50% (single core)

---

## Security Considerations

1. **Video Privacy:** All processing local, no cloud upload
2. **WebSocket:** Use WSS in production
3. **CORS:** Configure allowed origins
4. **Input Validation:** Check landmark format
5. **Rate Limiting:** Prevent abuse

---

## Future Enhancements

1. **Multi-person tracking**
2. **Exercise recommendations**
3. **Progress tracking dashboard**
4. **Social features (leaderboards)**
5. **Voice feedback**
6. **AR overlays**
7. **Wearable integration**

---

This architecture provides a solid foundation for a production-grade AI fitness trainer with room for extensive customization and scaling.
