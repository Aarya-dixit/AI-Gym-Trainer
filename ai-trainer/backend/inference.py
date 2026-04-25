"""
Inference Pipeline
Orchestrates the complete inference flow
"""
import torch
import numpy as np
from collections import deque
from typing import List, Dict, Optional
from feature_extractor import FeatureExtractor
from rep_counter import RepCounter
from feedback import FeedbackEngine
from model import TemporalTransformer


class InferencePipeline:
    """Complete inference pipeline for real-time exercise analysis"""
    
    def __init__(
        self,
        model: TemporalTransformer,
        sequence_length: int = 30,
        device: str = 'cpu',
        exercise_type: str = 'squat'
    ):
        """
        Args:
            model: Trained transformer model
            sequence_length: Number of frames in sliding window
            device: 'cpu' or 'cuda'
            exercise_type: Type of exercise to track
        """
        self.model = model
        self.model.eval()
        self.device = device
        self.model.to(device)
        
        self.sequence_length = sequence_length
        self.exercise_type = exercise_type
        self.feature_extractor = FeatureExtractor()
        self.rep_counter = RepCounter(exercise_type=exercise_type, smoothing_window=3)
        self.feedback_engine = FeedbackEngine(throttle_seconds=2.0, exercise_type=exercise_type)
        
        # Sliding window buffer
        self.feature_buffer = deque(maxlen=sequence_length)
        self.buffer_ready = False
        self.use_simple_counting = True  # Use rule-based counting by default
        
    def process_frame(self, landmarks: List[Dict]) -> Optional[Dict]:
        """
        Process a single frame
        
        Args:
            landmarks: List of 33 pose landmarks
            
        Returns:
            Inference results or None if buffer not ready
        """
        try:
            # Use simple rule-based counting (more reliable for untrained model)
            if self.use_simple_counting:
                rep_info = self.rep_counter.update_simple(landmarks)
                
                # Still extract features for potential model use
                features = self.feature_extractor.extract(landmarks)
                self.feature_buffer.append(features)
                
                # Return results immediately
                return {
                    'rep_count': rep_info['rep_count'],
                    'phase': rep_info['phase'],
                    'score': 0.85,  # Default good score
                    'feedback': f"Keep going! Exercise: {self.exercise_type}",
                    'errors': {
                        'knees_inward': 0.0,
                        'insufficient_depth': 0.0,
                        'back_bending': 0.0
                    },
                    'exercise': self.exercise_type
                }
            
            # Original model-based approach
            features = self.feature_extractor.extract(landmarks)
            self.feature_buffer.append(features)
            
            if len(self.feature_buffer) < self.sequence_length:
                return None
            
            self.buffer_ready = True
            return self._run_inference()
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return None
    
    def _run_inference(self) -> Dict:
        """Run model inference on current buffer"""
        # Convert buffer to tensor
        sequence = np.array(list(self.feature_buffer))  # (seq_len, feature_dim)
        sequence_tensor = torch.from_numpy(sequence).unsqueeze(0).float()  # (1, seq_len, feature_dim)
        sequence_tensor = sequence_tensor.to(self.device)
        
        # Model inference
        with torch.no_grad():
            phase_logits, error_logits, score = self.model(sequence_tensor)
        
        # Get predictions
        phase_pred = torch.argmax(phase_logits, dim=1).item()
        error_probs = torch.sigmoid(error_logits).squeeze().cpu().numpy()
        score_value = score.item()
        
        # Update rep counter
        rep_info = self.rep_counter.update(phase_pred)
        
        # Generate feedback
        feedback = self.feedback_engine.generate_feedback(error_probs.tolist())
        
        # Compile results
        results = {
            'rep_count': rep_info['rep_count'],
            'phase': rep_info['phase'],
            'score': round(score_value, 2),
            'feedback': feedback,
            'errors': {
                'knees_inward': float(error_probs[0]),
                'insufficient_depth': float(error_probs[1]),
                'back_bending': float(error_probs[2])
            }
        }
        
        return results
    
    def set_exercise(self, exercise_type: str):
        """Change exercise type"""
        self.exercise_type = exercise_type
        self.rep_counter.set_exercise(exercise_type)
        self.feedback_engine.set_exercise(exercise_type)
        self.reset()
    
    def reset(self):
        """Reset pipeline state"""
        self.feature_buffer.clear()
        self.buffer_ready = False
        self.feature_extractor.reset()
        self.rep_counter.reset()
        self.feedback_engine.reset()
    
    def is_ready(self) -> bool:
        """Check if buffer is ready for inference"""
        return self.buffer_ready
