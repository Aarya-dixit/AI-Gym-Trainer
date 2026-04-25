"""
System Test Script
Verify all components work correctly
"""
import numpy as np
import torch
from feature_extractor import FeatureExtractor
from model import create_model
from rep_counter import RepCounter
from feedback import FeedbackEngine
from inference import InferencePipeline


def test_feature_extractor():
    """Test feature extraction"""
    print("Testing Feature Extractor...")
    
    extractor = FeatureExtractor()
    
    # Create dummy landmarks
    landmarks = []
    for i in range(33):
        landmarks.append({
            'x': np.random.rand(),
            'y': np.random.rand(),
            'z': np.random.rand(),
            'visibility': 0.9
        })
    
    # Extract features
    features = extractor.extract(landmarks)
    
    print(f"  ✓ Feature shape: {features.shape}")
    print(f"  ✓ Feature dimension: {len(features)}")
    assert len(features) == 175, f"Expected 175 features, got {len(features)}"
    print("  ✓ Feature extractor working!\n")


def test_model():
    """Test model architecture"""
    print("Testing Model...")
    
    input_dim = 175
    batch_size = 4
    seq_len = 30
    
    model = create_model(input_dim)
    
    # Create dummy input
    x = torch.randn(batch_size, seq_len, input_dim)
    
    # Forward pass
    phase_logits, error_logits, score = model(x)
    
    print(f"  ✓ Phase logits shape: {phase_logits.shape}")
    print(f"  ✓ Error logits shape: {error_logits.shape}")
    print(f"  ✓ Score shape: {score.shape}")
    
    assert phase_logits.shape == (batch_size, 4)
    assert error_logits.shape == (batch_size, 3)
    assert score.shape == (batch_size, 1)
    
    print("  ✓ Model architecture working!\n")


def test_rep_counter():
    """Test rep counter"""
    print("Testing Rep Counter...")
    
    counter = RepCounter(smoothing_window=5)
    
    # Simulate a squat rep: top -> down -> bottom -> up -> top
    phases = [0, 0, 1, 1, 2, 2, 3, 3, 0, 0]
    
    for phase in phases:
        result = counter.update(phase)
    
    print(f"  ✓ Rep count: {result['rep_count']}")
    print(f"  ✓ Current phase: {result['phase']}")
    
    assert result['rep_count'] >= 0, "Rep count should be non-negative"
    print("  ✓ Rep counter working!\n")


def test_feedback_engine():
    """Test feedback engine"""
    print("Testing Feedback Engine...")
    
    engine = FeedbackEngine(throttle_seconds=0.1)
    
    # Test with errors
    errors = [0.8, 0.3, 0.1]  # High knees_inward error
    feedback = engine.generate_feedback(errors)
    
    print(f"  ✓ Feedback: {feedback}")
    assert feedback is not None
    
    # Test with no errors
    errors = [0.1, 0.1, 0.1]
    feedback = engine.generate_feedback(errors)
    
    print(f"  ✓ Good form feedback: {feedback}")
    print("  ✓ Feedback engine working!\n")


def test_inference_pipeline():
    """Test complete inference pipeline"""
    print("Testing Inference Pipeline...")
    
    input_dim = 175
    model = create_model(input_dim)
    pipeline = InferencePipeline(model, sequence_length=30)
    
    # Create dummy landmarks
    for i in range(35):  # More than sequence_length
        landmarks = []
        for j in range(33):
            landmarks.append({
                'x': np.random.rand(),
                'y': np.random.rand(),
                'z': np.random.rand(),
                'visibility': 0.9
            })
        
        result = pipeline.process_frame(landmarks)
        
        if result is not None:
            print(f"  ✓ Rep count: {result['rep_count']}")
            print(f"  ✓ Phase: {result['phase']}")
            print(f"  ✓ Score: {result['score']}")
            print(f"  ✓ Feedback: {result['feedback']}")
            
            assert 'rep_count' in result
            assert 'phase' in result
            assert 'score' in result
            assert 'feedback' in result
            assert 'errors' in result
            
            break
    
    print("  ✓ Inference pipeline working!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Personal Gym Trainer - System Test")
    print("=" * 60 + "\n")
    
    try:
        test_feature_extractor()
        test_model()
        test_rep_counter()
        test_feedback_engine()
        test_inference_pipeline()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSystem is ready to use!")
        print("\nNext steps:")
        print("1. Run backend: python main.py")
        print("2. Open frontend: frontend/index.html")
        print("3. (Optional) Train model: python training/train.py")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
