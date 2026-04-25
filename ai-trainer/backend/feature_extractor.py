"""
Feature Extractor Module
Converts MediaPipe pose landmarks into feature vectors
"""
import numpy as np
from typing import List, Dict, Tuple


class FeatureExtractor:
    """Extract skeletal features from MediaPipe pose landmarks"""
    
    # MediaPipe landmark indices
    LANDMARK_INDICES = {
        'nose': 0, 'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
        'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
        'left_ear': 7, 'right_ear': 8, 'mouth_left': 9, 'mouth_right': 10,
        'left_shoulder': 11, 'right_shoulder': 12,
        'left_elbow': 13, 'right_elbow': 14,
        'left_wrist': 15, 'right_wrist': 16,
        'left_pinky': 17, 'right_pinky': 18,
        'left_index': 19, 'right_index': 20,
        'left_thumb': 21, 'right_thumb': 22,
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28,
        'left_heel': 29, 'right_heel': 30,
        'left_foot_index': 31, 'right_foot_index': 32
    }
    
    def __init__(self):
        self.prev_landmarks = None
        
    def extract(self, landmarks: List[Dict]) -> np.ndarray:
        """
        Extract features from pose landmarks
        
        Args:
            landmarks: List of 33 landmarks with x, y, z, visibility
            
        Returns:
            Feature vector of shape (feature_dim,)
        """
        if len(landmarks) != 33:
            raise ValueError(f"Expected 33 landmarks, got {len(landmarks)}")
        
        # Convert to numpy array
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        visibility = np.array([lm.get('visibility', 1.0) for lm in landmarks])
        
        # Normalize pose
        normalized_coords = self._normalize_pose(coords)
        
        # Extract features
        features = []
        
        # 1. Joint angles
        angles = self._compute_angles(normalized_coords)
        features.extend(angles)
        
        # 2. Bone vectors
        vectors = self._compute_bone_vectors(normalized_coords)
        features.extend(vectors.flatten())
        
        # 3. Velocity (if previous frame exists)
        if self.prev_landmarks is not None:
            velocity = self._compute_velocity(normalized_coords, self.prev_landmarks)
            features.extend(velocity.flatten())
        else:
            features.extend(np.zeros(33 * 3))  # Zero velocity for first frame
        
        # 4. Visibility scores
        features.extend(visibility)
        
        self.prev_landmarks = normalized_coords.copy()
        
        return np.array(features, dtype=np.float32)
    
    def _normalize_pose(self, coords: np.ndarray) -> np.ndarray:
        """Normalize pose by centering at hip and scaling by torso length"""
        # Hip center
        left_hip = coords[self.LANDMARK_INDICES['left_hip']]
        right_hip = coords[self.LANDMARK_INDICES['right_hip']]
        hip_center = (left_hip + right_hip) / 2
        
        # Translate to origin
        normalized = coords - hip_center
        
        # Compute torso length for scaling
        left_shoulder = coords[self.LANDMARK_INDICES['left_shoulder']]
        right_shoulder = coords[self.LANDMARK_INDICES['right_shoulder']]
        shoulder_center = (left_shoulder + right_shoulder) / 2
        torso_length = np.linalg.norm(shoulder_center - hip_center)
        
        # Scale
        if torso_length > 0:
            normalized = normalized / torso_length
        
        return normalized
    
    def _compute_angles(self, coords: np.ndarray) -> List[float]:
        """Compute joint angles"""
        angles = []
        
        # Left knee angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['left_hip']],
            coords[self.LANDMARK_INDICES['left_knee']],
            coords[self.LANDMARK_INDICES['left_ankle']]
        ))
        
        # Right knee angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['right_hip']],
            coords[self.LANDMARK_INDICES['right_knee']],
            coords[self.LANDMARK_INDICES['right_ankle']]
        ))
        
        # Left elbow angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['left_shoulder']],
            coords[self.LANDMARK_INDICES['left_elbow']],
            coords[self.LANDMARK_INDICES['left_wrist']]
        ))
        
        # Right elbow angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['right_shoulder']],
            coords[self.LANDMARK_INDICES['right_elbow']],
            coords[self.LANDMARK_INDICES['right_wrist']]
        ))
        
        # Left hip angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['left_shoulder']],
            coords[self.LANDMARK_INDICES['left_hip']],
            coords[self.LANDMARK_INDICES['left_knee']]
        ))
        
        # Right hip angle
        angles.append(self._angle_between_points(
            coords[self.LANDMARK_INDICES['right_shoulder']],
            coords[self.LANDMARK_INDICES['right_hip']],
            coords[self.LANDMARK_INDICES['right_knee']]
        ))
        
        # Back angle (torso)
        left_shoulder = coords[self.LANDMARK_INDICES['left_shoulder']]
        right_shoulder = coords[self.LANDMARK_INDICES['right_shoulder']]
        shoulder_center = (left_shoulder + right_shoulder) / 2
        left_hip = coords[self.LANDMARK_INDICES['left_hip']]
        right_hip = coords[self.LANDMARK_INDICES['right_hip']]
        hip_center = (left_hip + right_hip) / 2
        
        # Angle of torso with vertical
        torso_vector = shoulder_center - hip_center
        vertical = np.array([0, -1, 0])
        angles.append(self._angle_between_vectors(torso_vector, vertical))
        
        return angles
    
    def _angle_between_points(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate angle at p2 formed by p1-p2-p3"""
        v1 = p1 - p2
        v2 = p3 - p2
        return self._angle_between_vectors(v1, v2)
    
    def _angle_between_vectors(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle between two vectors in degrees"""
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        return np.degrees(angle)
    
    def _compute_bone_vectors(self, coords: np.ndarray) -> np.ndarray:
        """Compute bone vectors between connected joints"""
        vectors = []
        
        # Define bone connections
        bones = [
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_shoulder', 'right_shoulder'),
            ('left_hip', 'right_hip'),
        ]
        
        for joint1, joint2 in bones:
            idx1 = self.LANDMARK_INDICES[joint1]
            idx2 = self.LANDMARK_INDICES[joint2]
            vector = coords[idx2] - coords[idx1]
            vectors.append(vector)
        
        return np.array(vectors)
    
    def _compute_velocity(self, current: np.ndarray, previous: np.ndarray) -> np.ndarray:
        """Compute velocity as difference between frames"""
        return current - previous
    
    def reset(self):
        """Reset previous landmarks"""
        self.prev_landmarks = None
