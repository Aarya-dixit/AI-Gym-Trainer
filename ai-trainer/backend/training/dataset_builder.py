"""
Dataset Builder
Process videos to extract skeleton sequences for training
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import sys
sys.path.append(str(Path(__file__).parent.parent))
from feature_extractor import FeatureExtractor
from mediapipe_compat import mp_pose


class DatasetBuilder:
    """Build training dataset from videos"""
    
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.feature_extractor = FeatureExtractor()
    
    def process_video(self, video_path: str) -> np.ndarray:
        """
        Extract skeleton features from video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Array of shape (num_frames, feature_dim)
        """
        cap = cv2.VideoCapture(video_path)
        features_list = []
        
        self.feature_extractor.reset()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # Convert to landmark dict format
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': lm.x,
                        'y': lm.y,
                        'z': lm.z,
                        'visibility': lm.visibility
                    })
                
                # Extract features
                try:
                    features = self.feature_extractor.extract(landmarks)
                    features_list.append(features)
                except Exception as e:
                    print(f"Error extracting features: {e}")
                    continue
        
        cap.release()
        
        if len(features_list) == 0:
            raise ValueError(f"No valid frames extracted from {video_path}")
        
        return np.array(features_list)
    
    def create_sequences(
        self,
        features: np.ndarray,
        labels: dict,
        sequence_length: int = 30,
        stride: int = 15
    ) -> Tuple[np.ndarray, dict]:
        """
        Create sliding window sequences from features
        
        Args:
            features: Array of shape (num_frames, feature_dim)
            labels: Dict with 'phase', 'errors', 'score' arrays
            sequence_length: Length of each sequence
            stride: Stride for sliding window
            
        Returns:
            sequences: (num_sequences, sequence_length, feature_dim)
            sequence_labels: Dict with label arrays
        """
        num_frames = len(features)
        sequences = []
        phase_labels = []
        error_labels = []
        score_labels = []
        
        for i in range(0, num_frames - sequence_length + 1, stride):
            seq = features[i:i + sequence_length]
            sequences.append(seq)
            
            # Use label from middle of sequence
            mid_idx = i + sequence_length // 2
            phase_labels.append(labels['phase'][mid_idx])
            error_labels.append(labels['errors'][mid_idx])
            score_labels.append(labels['score'][mid_idx])
        
        return (
            np.array(sequences),
            {
                'phase': np.array(phase_labels),
                'errors': np.array(error_labels),
                'score': np.array(score_labels)
            }
        )
    
    def build_dataset(
        self,
        video_dir: str,
        output_dir: str,
        sequence_length: int = 30
    ):
        """
        Build complete dataset from video directory
        
        Expected structure:
        video_dir/
            video1.mp4
            video1_labels.npy  # Contains phase, errors, score per frame
            video2.mp4
            video2_labels.npy
            ...
        """
        video_dir = Path(video_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        all_sequences = []
        all_phase_labels = []
        all_error_labels = []
        all_score_labels = []
        
        # Process each video
        for video_path in video_dir.glob("*.mp4"):
            label_path = video_path.with_suffix('').with_name(f"{video_path.stem}_labels.npy")
            
            if not label_path.exists():
                print(f"Warning: No labels found for {video_path.name}, skipping")
                continue
            
            print(f"Processing {video_path.name}...")
            
            # Extract features
            features = self.process_video(str(video_path))
            
            # Load labels
            labels = np.load(label_path, allow_pickle=True).item()
            
            # Create sequences
            sequences, seq_labels = self.create_sequences(
                features, labels, sequence_length
            )
            
            all_sequences.append(sequences)
            all_phase_labels.append(seq_labels['phase'])
            all_error_labels.append(seq_labels['errors'])
            all_score_labels.append(seq_labels['score'])
        
        # Concatenate all
        all_sequences = np.concatenate(all_sequences, axis=0)
        all_phase_labels = np.concatenate(all_phase_labels, axis=0)
        all_error_labels = np.concatenate(all_error_labels, axis=0)
        all_score_labels = np.concatenate(all_score_labels, axis=0)
        
        # Save dataset
        np.save(output_dir / "sequences.npy", all_sequences)
        np.save(output_dir / "phase_labels.npy", all_phase_labels)
        np.save(output_dir / "error_labels.npy", all_error_labels)
        np.save(output_dir / "score_labels.npy", all_score_labels)
        
        print(f"\nDataset created:")
        print(f"  Sequences: {all_sequences.shape}")
        print(f"  Saved to: {output_dir}")


if __name__ == "__main__":
    # Example usage
    builder = DatasetBuilder()
    builder.build_dataset(
        video_dir="data/videos",
        output_dir="data/videos",
        sequence_length=30
    )
