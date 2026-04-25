"""
Rep Counter Module
Deterministic state machine for counting exercise repetitions
Supports multiple exercises: squat, boxing, waving, jumping
"""
from collections import deque
from typing import Optional
import numpy as np


class RepCounter:
    """State machine for counting repetitions across multiple exercises"""
    
    # Exercise types
    EXERCISE_SQUAT = "squat"
    EXERCISE_BOXING = "boxing"
    EXERCISE_WAVING = "waving"
    EXERCISE_JUMPING = "jumping"
    
    # Phase constants
    PHASE_TOP = 0
    PHASE_DOWN = 1
    PHASE_BOTTOM = 2
    PHASE_UP = 3
    
    PHASE_NAMES = {
        0: "ready",
        1: "down",
        2: "low",
        3: "up"
    }
    
    def __init__(self, exercise_type: str = EXERCISE_SQUAT, smoothing_window: int = 3):
        """
        Args:
            exercise_type: Type of exercise to track
            smoothing_window: Number of predictions to smooth over
        """
        self.exercise_type = exercise_type
        self.smoothing_window = smoothing_window
        self.phase_buffer = deque(maxlen=smoothing_window)
        self.current_phase = self.PHASE_TOP
        self.rep_count = 0
        self.in_rep = False
        self.last_transition = None
        
    def update(self, phase_prediction: int) -> dict:
        """
        Update state machine with new phase prediction
        
        Args:
            phase_prediction: Predicted phase (0-3)
            
        Returns:
            dict with rep_count, phase, phase_changed
        """
        # Add to buffer
        self.phase_buffer.append(phase_prediction)
        
        # Smooth prediction
        if len(self.phase_buffer) >= self.smoothing_window:
            smoothed_phase = self._get_smoothed_phase()
        else:
            smoothed_phase = phase_prediction
        
        # State machine logic
        phase_changed = False
        if smoothed_phase != self.current_phase:
            phase_changed = True
            prev_phase = self.current_phase
            self.current_phase = smoothed_phase
            self.last_transition = (prev_phase, self.current_phase)
            
            # Check for rep completion based on exercise type
            if self._is_rep_complete(prev_phase, self.current_phase):
                self.rep_count += 1
        
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'phase_changed': phase_changed
        }
    
    def update_simple(self, landmarks: list) -> dict:
        """
        Simple rule-based rep counting using landmark positions
        More reliable than model predictions for untrained models
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            dict with rep_count, phase, phase_changed
        """
        if self.exercise_type == self.EXERCISE_SQUAT:
            return self._count_squat(landmarks)
        elif self.exercise_type == self.EXERCISE_BOXING:
            return self._count_boxing(landmarks)
        elif self.exercise_type == self.EXERCISE_WAVING:
            return self._count_waving(landmarks)
        elif self.exercise_type == self.EXERCISE_JUMPING:
            return self._count_jumping(landmarks)
        else:
            return self.get_state()
    
    def _count_squat(self, landmarks: list) -> dict:
        """Count squats based on hip and knee height"""
        # Get key landmarks
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_knee = landmarks[25]
        right_knee = landmarks[26]
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        
        # Calculate hip height relative to ankles
        hip_y = (left_hip['y'] + right_hip['y']) / 2
        ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
        knee_y = (left_knee['y'] + right_knee['y']) / 2
        
        # Determine phase based on relative positions
        hip_knee_dist = abs(hip_y - knee_y)
        
        phase_changed = False
        prev_phase = self.current_phase
        
        # Thresholds (normalized coordinates)
        if hip_knee_dist < 0.15:  # Very close - bottom position
            self.current_phase = self.PHASE_BOTTOM
        elif hip_y > knee_y - 0.05:  # Hip below knee - going down
            self.current_phase = self.PHASE_DOWN
        elif hip_y < knee_y - 0.2:  # Hip well above knee - top position
            self.current_phase = self.PHASE_TOP
        else:  # Coming up
            self.current_phase = self.PHASE_UP
        
        # Detect rep completion: bottom -> up transition
        if prev_phase == self.PHASE_BOTTOM and self.current_phase == self.PHASE_UP:
            self.rep_count += 1
            phase_changed = True
        elif prev_phase != self.current_phase:
            phase_changed = True
        
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'phase_changed': phase_changed
        }
    
    def _count_boxing(self, landmarks: list) -> dict:
        """Count boxing punches based on hand extension"""
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        nose = landmarks[0]
        
        # Calculate hand extension
        left_extend = abs(left_wrist['x'] - left_shoulder['x'])
        right_extend = abs(right_wrist['x'] - right_shoulder['x'])
        
        phase_changed = False
        prev_phase = self.current_phase
        
        # Check if either hand is extended (punch)
        if left_extend > 0.3 or right_extend > 0.3:
            self.current_phase = self.PHASE_UP  # Extended
        else:
            self.current_phase = self.PHASE_TOP  # Retracted
        
        # Count rep on extension
        if prev_phase == self.PHASE_TOP and self.current_phase == self.PHASE_UP:
            self.rep_count += 1
            phase_changed = True
        elif prev_phase != self.current_phase:
            phase_changed = True
        
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'phase_changed': phase_changed
        }
    
    def _count_waving(self, landmarks: list) -> dict:
        """Count waves based on hand height"""
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        
        # Check if hand is above shoulder (waving)
        left_wave = left_wrist['y'] < left_shoulder['y'] - 0.1
        right_wave = right_wrist['y'] < right_shoulder['y'] - 0.1
        
        phase_changed = False
        prev_phase = self.current_phase
        
        if left_wave or right_wave:
            self.current_phase = self.PHASE_UP  # Hand up
        else:
            self.current_phase = self.PHASE_TOP  # Hand down
        
        # Count rep on hand raise
        if prev_phase == self.PHASE_TOP and self.current_phase == self.PHASE_UP:
            self.rep_count += 1
            phase_changed = True
        elif prev_phase != self.current_phase:
            phase_changed = True
        
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'phase_changed': phase_changed
        }
    
    def _count_jumping(self, landmarks: list) -> dict:
        """Count jumps based on foot height"""
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Calculate ankle height relative to hip
        ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
        hip_y = (left_hip['y'] + right_hip['y']) / 2
        
        leg_length = abs(ankle_y - hip_y)
        
        phase_changed = False
        prev_phase = self.current_phase
        
        # Detect jump (legs extended, body elevated)
        if leg_length < 0.4:  # Compressed - preparing or landing
            self.current_phase = self.PHASE_BOTTOM
        elif leg_length > 0.5:  # Extended - in air
            self.current_phase = self.PHASE_UP
        else:
            self.current_phase = self.PHASE_DOWN
        
        # Count rep on landing
        if prev_phase == self.PHASE_UP and self.current_phase == self.PHASE_BOTTOM:
            self.rep_count += 1
            phase_changed = True
        elif prev_phase != self.current_phase:
            phase_changed = True
        
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'phase_changed': phase_changed
        }
    
    def _get_smoothed_phase(self) -> int:
        """Get most common phase in buffer"""
        if not self.phase_buffer:
            return self.PHASE_TOP
        
        # Count occurrences
        counts = [0] * 4
        for phase in self.phase_buffer:
            counts[phase] += 1
        
        # Return most common
        return counts.index(max(counts))
    
    def _is_rep_complete(self, prev_phase: int, current_phase: int) -> bool:
        """
        Check if a repetition is complete
        
        For squat: top → down → bottom → up → top
        Rep completes on bottom → up transition
        """
        # Transition from bottom to up indicates rep completion
        if prev_phase == self.PHASE_BOTTOM and current_phase == self.PHASE_UP:
            return True
        
        return False
    
    def set_exercise(self, exercise_type: str):
        """Change exercise type"""
        self.exercise_type = exercise_type
        self.reset()
    
    def reset(self):
        """Reset counter"""
        self.phase_buffer.clear()
        self.current_phase = self.PHASE_TOP
        self.rep_count = 0
        self.in_rep = False
        self.last_transition = None
    
    def get_state(self) -> dict:
        """Get current state"""
        return {
            'rep_count': self.rep_count,
            'phase': self.PHASE_NAMES[self.current_phase],
            'in_rep': self.in_rep,
            'exercise': self.exercise_type
        }
