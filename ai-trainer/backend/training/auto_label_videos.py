"""
Auto-Label Videos for Training
Automatically generates labels for recorded exercise videos using rule-based detection
"""
import cv2
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from rep_counter import RepCounter
from mediapipe_compat import mp_pose


class VideoLabeler:
    """Automatically label exercise videos"""
    
    def __init__(self, exercise_type: str = 'squat'):
        """
        Args:
            exercise_type: Type of exercise (squat, boxing, waving, jumping)
        """
        self.exercise_type = exercise_type
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.rep_counter = RepCounter(exercise_type=exercise_type, smoothing_window=3)
    
    def label_video(self, video_path: str) -> dict:
        """
        Automatically label a video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with phase, errors, and score labels
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Cannot open video {video_path}")
            return None
        
        phase_labels = []
        error_labels = []
        score_labels = []
        frame_count = 0
        
        print(f"Processing {Path(video_path).name}...")
        
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
                
                # Get rep counter state
                rep_info = self.rep_counter.update_simple(landmarks)
                
                # Extract phase
                phase = self._phase_to_label(rep_info['phase'])
                phase_labels.append(phase)
                
                # Estimate errors (simplified)
                errors = self._estimate_errors(landmarks)
                error_labels.append(errors)
                
                # Estimate score (simplified)
                score = self._estimate_score(landmarks)
                score_labels.append(score)
                
                frame_count += 1
                
                if frame_count % 30 == 0:
                    print(f"  Processed {frame_count} frames...")
        
        cap.release()
        
        if frame_count == 0:
            print(f"Error: No valid frames in {video_path}")
            return None
        
        print(f"  Total frames: {frame_count}")
        print(f"  Reps detected: {self.rep_counter.rep_count}")
        
        return {
            'phase': np.array(phase_labels),
            'errors': np.array(error_labels),
            'score': np.array(score_labels)
        }
    
    def _phase_to_label(self, phase_name: str) -> int:
        """Convert phase name to label"""
        phase_map = {
            'ready': 0,
            'down': 1,
            'low': 2,
            'up': 3
        }
        return phase_map.get(phase_name, 0)
    
    def _estimate_errors(self, landmarks: list) -> list:
        """Estimate errors from landmarks"""
        errors = [0, 0, 0]  # [knees_inward, insufficient_depth, back_bending]
        
        if self.exercise_type == 'squat':
            # Check for knees inward
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            # Simple heuristic: if knees are closer than ankles
            knee_dist = abs(left_knee['x'] - right_knee['x'])
            ankle_dist = abs(left_ankle['x'] - right_ankle['x'])
            
            if knee_dist < ankle_dist * 0.7:
                errors[0] = 1  # Knees inward
            
            # Check for back bending
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
            hip_y = (left_hip['y'] + right_hip['y']) / 2
            
            # If shoulder moves too far forward
            shoulder_x = (left_shoulder['x'] + right_shoulder['x']) / 2
            hip_x = (left_hip['x'] + right_hip['x']) / 2
            
            if abs(shoulder_x - hip_x) > 0.15:
                errors[2] = 1  # Back bending
        
        return errors
    
    def _estimate_score(self, landmarks: list) -> float:
        """Estimate form score from landmarks"""
        # Simple heuristic: based on visibility and stability
        visibility_scores = [lm.get('visibility', 1.0) for lm in landmarks]
        avg_visibility = np.mean(visibility_scores)
        
        # Score based on visibility (0.5 to 1.0)
        score = 0.5 + (avg_visibility * 0.5)
        
        return min(1.0, max(0.0, score))
    
    def reset(self):
        """Reset for next video"""
        self.rep_counter.reset()


def label_dataset(video_dir: str, output_dir: str, exercise_type: str = 'squat'):
    """
    Label all videos in a directory
    
    Args:
        video_dir: Directory containing videos
        output_dir: Directory to save labels
        exercise_type: Type of exercise
    """
    video_dir = Path(video_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    labeler = VideoLabeler(exercise_type=exercise_type)
    
    # Find all video files
    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi")) + list(video_dir.glob("*.mov"))
    
    if not video_files:
        print(f"No video files found in {video_dir}")
        return
    
    print(f"Found {len(video_files)} videos to label")
    print(f"Exercise type: {exercise_type}\n")
    
    for video_path in video_files:
        print(f"\nProcessing: {video_path.name}")
        
        # Label video
        labels = labeler.label_video(str(video_path))
        
        if labels is not None:
            # Save labels
            label_path = output_dir / f"{video_path.stem}_labels.npy"
            np.save(label_path, labels)
            print(f"  Saved labels to {label_path.name}")
        
        # Reset for next video
        labeler.reset()
    
    print(f"\n✅ Labeling complete! Labels saved to {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-label exercise videos')
    parser.add_argument('--video-dir', default='data/videos', help='Directory with videos')
    parser.add_argument('--output-dir', default='data/videos', help='Directory to save labels')
    parser.add_argument('--exercise', default='squat', help='Exercise type: squat, boxing, waving, jumping')
    
    args = parser.parse_args()
    
    label_dataset(args.video_dir, args.output_dir, args.exercise)
