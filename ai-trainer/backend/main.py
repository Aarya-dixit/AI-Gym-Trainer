"""
FastAPI Backend Server
WebSocket endpoint for real-time pose analysis
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
import json
import os
from pathlib import Path
from inference import InferencePipeline
from model import create_model


app = FastAPI(title="AI Personal Gym Trainer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global inference pipeline
pipeline = None
model_loaded = False


def load_model():
    """Load trained model or create untrained model"""
    global pipeline, model_loaded
    
    model_path = Path(__file__).parent.parent / "models" / "model.pt"
    
    # Determine feature dimension (from feature extractor)
    # 7 angles + 12*3 bone vectors + 33*3 velocity + 33 visibility = 7 + 36 + 99 + 33 = 175
    input_dim = 175
    
    model = create_model(input_dim)
    
    if model_path.exists():
        print(f"Loading model from {model_path}")
        checkpoint = torch.load(model_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        print("Model loaded successfully")
    else:
        print("No trained model found. Using untrained model.")
        print("Train the model using training/train.py")
    
    pipeline = InferencePipeline(model, sequence_length=30, device='cpu')
    model_loaded = True


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    load_model()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model_loaded": model_loaded,
        "message": "AI Personal Gym Trainer API"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "model_loaded": model_loaded}


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time pose analysis
    
    Input format:
    {
        "landmarks": [...],
        "exercise": "squat" | "boxing" | "waving" | "jumping"  (optional)
    }
    
    Output format:
    {
        "rep_count": int,
        "phase": str,
        "score": float,
        "feedback": str,
        "exercise": str,
        "errors": {...}
    }
    """
    await websocket.accept()
    print("Client connected")
    
    # Reset pipeline for new session
    if pipeline:
        pipeline.reset()
    
    current_exercise = 'squat'  # Default exercise
    
    try:
        while True:
            # Receive landmarks
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Check for exercise change
            if "exercise" in message and message["exercise"]:
                new_exercise = message["exercise"]
                if new_exercise != current_exercise:
                    current_exercise = new_exercise
                    if pipeline:
                        pipeline.set_exercise(new_exercise)
                        print(f"Exercise changed to: {new_exercise}")
            
            if "landmarks" not in message:
                await websocket.send_json({
                    "error": "Missing landmarks field"
                })
                continue
            
            landmarks = message["landmarks"]
            
            # Validate landmarks
            if len(landmarks) != 33:
                await websocket.send_json({
                    "error": f"Expected 33 landmarks, got {len(landmarks)}"
                })
                continue
            
            # Process frame
            result = pipeline.process_frame(landmarks)
            
            if result is None:
                # Buffer not ready yet
                await websocket.send_json({
                    "status": "buffering",
                    "message": "Collecting frames..."
                })
            else:
                # Ensure exercise is in result
                result['exercise'] = current_exercise
                # Send results
                await websocket.send_json(result)
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"error": str(e)})


@app.post("/reset")
async def reset_session():
    """Reset the inference pipeline"""
    if pipeline:
        pipeline.reset()
    return {"status": "reset"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
