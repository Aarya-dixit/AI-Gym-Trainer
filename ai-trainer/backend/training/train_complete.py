"""
Complete Training Workflow
End-to-end pipeline: videos → labels → dataset → training
"""
import os
import sys
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, random_split

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dataset_builder import DatasetBuilder, ExerciseDataset
from train import Trainer
from model import create_model


def setup_directories():
    """Create necessary directories"""
    dirs = [
        'data/videos',
        'data/processed',
        '../../models'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {dir_path}")


def step1_auto_label_videos(video_dir: str, exercise_type: str = 'squat'):
    """Step 1: Auto-label videos"""
    print("\n" + "="*60)
    print("STEP 1: AUTO-LABELING VIDEOS")
    print("="*60)
    
    from auto_label_videos import label_dataset
    
    print(f"Looking for videos in: {video_dir}")
    print(f"Exercise type: {exercise_type}")
    
    label_dataset(video_dir, video_dir, exercise_type)
    
    print("✓ Videos labeled successfully!")


def step2_build_dataset(video_dir: str, output_dir: str, sequence_length: int = 30):
    """Step 2: Build dataset from labeled videos"""
    print("\n" + "="*60)
    print("STEP 2: BUILDING DATASET")
    print("="*60)
    
    builder = DatasetBuilder()
    builder.build_dataset(video_dir, output_dir, sequence_length)
    
    print("✓ Dataset built successfully!")


def step3_train_model(data_dir: str, model_save_path: str, num_epochs: int = 30):
    """Step 3: Train the model"""
    print("\n" + "="*60)
    print("STEP 3: TRAINING MODEL")
    print("="*60)
    
    # Load dataset
    print("Loading dataset...")
    dataset = ExerciseDataset(data_dir)
    
    # Split into train/val
    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    print(f"Train size: {train_size}, Val size: {val_size}")
    
    # Create dataloaders
    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Get input dimension
    sample_batch = next(iter(train_loader))
    input_dim = sample_batch['sequence'].shape[-1]
    print(f"Input dimension: {input_dim}")
    
    # Create model
    print("Creating model...")
    model = create_model(input_dim)
    
    # Count parameters
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {num_params:,}")
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        lr=1e-3
    )
    
    # Train
    print(f"\nTraining for {num_epochs} epochs...")
    trainer.train(num_epochs=num_epochs, save_path=model_save_path)
    
    print("✓ Model trained successfully!")
    print(f"✓ Model saved to: {model_save_path}")


def main():
    """Main training workflow"""
    print("\n" + "="*60)
    print("AI PERSONAL GYM TRAINER - COMPLETE TRAINING WORKFLOW")
    print("="*60)
    
    # Configuration
    VIDEO_DIR = 'data/videos'
    OUTPUT_DIR = 'data/processed'
    MODEL_SAVE_PATH = '../../models/model.pt'
    EXERCISE_TYPE = 'squat'  # Change to: boxing, waving, jumping
    NUM_EPOCHS = 30
    
    print(f"\nConfiguration:")
    print(f"  Video directory: {VIDEO_DIR}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Model save path: {MODEL_SAVE_PATH}")
    print(f"  Exercise type: {EXERCISE_TYPE}")
    print(f"  Epochs: {NUM_EPOCHS}")
    
    # Setup
    print("\nSetting up directories...")
    setup_directories()
    
    # Check if videos exist
    video_files = list(Path(VIDEO_DIR).glob("*.mp4")) + \
                  list(Path(VIDEO_DIR).glob("*.avi")) + \
                  list(Path(VIDEO_DIR).glob("*.mov"))
    
    if not video_files:
        print(f"\n⚠️  No videos found in {VIDEO_DIR}")
        print("Please record videos and place them in the data/videos directory")
        print("\nExample:")
        print("  1. Record squat videos: squat_1.mp4, squat_2.mp4, squat_3.mp4")
        print("  2. Place in: data/videos/")
        print("  3. Run this script again")
        return
    
    print(f"✓ Found {len(video_files)} videos")
    
    # Step 1: Auto-label videos
    try:
        step1_auto_label_videos(VIDEO_DIR, EXERCISE_TYPE)
    except Exception as e:
        print(f"✗ Error in step 1: {e}")
        return
    
    # Step 2: Build dataset
    try:
        step2_build_dataset(VIDEO_DIR, OUTPUT_DIR)
    except Exception as e:
        print(f"✗ Error in step 2: {e}")
        return
    
    # Step 3: Train model
    try:
        step3_train_model(OUTPUT_DIR, MODEL_SAVE_PATH, NUM_EPOCHS)
    except Exception as e:
        print(f"✗ Error in step 3: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"\nYour trained model is ready at: {MODEL_SAVE_PATH}")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. The new model will be loaded automatically")
    print("3. Test with your exercises!")


if __name__ == "__main__":
    main()
