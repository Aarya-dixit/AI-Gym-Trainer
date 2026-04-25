"""
Feedback Engine
Maps form errors to user-friendly feedback messages
Supports multiple exercises: squat, boxing, waving, jumping
"""
import time
from typing import List, Optional


class FeedbackEngine:
    """Generate real-time feedback based on form errors and exercise type"""
    
    # Error indices
    ERROR_KNEES_INWARD = 0
    ERROR_INSUFFICIENT_DEPTH = 1
    ERROR_BACK_BENDING = 2
    
    # Generic error messages
    ERROR_MESSAGES = {
        ERROR_KNEES_INWARD: "Keep knees aligned with toes",
        ERROR_INSUFFICIENT_DEPTH: "Go lower",
        ERROR_BACK_BENDING: "Keep your back straight"
    }
    
    # Error priorities (higher = more important)
    ERROR_PRIORITIES = {
        ERROR_BACK_BENDING: 3,
        ERROR_KNEES_INWARD: 2,
        ERROR_INSUFFICIENT_DEPTH: 1
    }
    
    # Exercise-specific encouragement messages
    ENCOURAGEMENT = {
        'squat': [
            "Great form! Keep it up!",
            "Excellent depth!",
            "Perfect control!",
            "Nice and steady!",
            "You're doing great!"
        ],
        'boxing': [
            "Powerful punch!",
            "Great speed!",
            "Excellent form!",
            "Keep those hands up!",
            "Nice combinations!"
        ],
        'waving': [
            "Smooth motion!",
            "Great rhythm!",
            "Perfect wave!",
            "Nice and controlled!",
            "Keep it flowing!"
        ],
        'jumping': [
            "Great height!",
            "Explosive power!",
            "Perfect landing!",
            "Nice and bouncy!",
            "Excellent form!"
        ]
    }
    
    # Exercise-specific tips
    TIPS = {
        'squat': "Keep your chest up and core engaged",
        'boxing': "Rotate your hips with each punch",
        'waving': "Keep your arm relaxed and smooth",
        'jumping': "Land softly with bent knees"
    }
    
    def __init__(self, throttle_seconds: float = 2.0, error_threshold: float = 0.5, exercise_type: str = 'squat'):
        """
        Args:
            throttle_seconds: Minimum time between feedback messages
            error_threshold: Threshold for error detection (0-1)
            exercise_type: Type of exercise being performed
        """
        self.throttle_seconds = throttle_seconds
        self.error_threshold = error_threshold
        self.exercise_type = exercise_type
        self.last_feedback_time = 0
        self.last_feedback_message = ""
        self.encouragement_index = 0
        
    def generate_feedback(self, error_predictions: List[float]) -> Optional[str]:
        """
        Generate feedback message based on error predictions
        
        Args:
            error_predictions: List of error probabilities [knees_inward, insufficient_depth, back_bending]
            
        Returns:
            Feedback message or None if throttled
        """
        current_time = time.time()
        
        # Check throttle
        if current_time - self.last_feedback_time < self.throttle_seconds:
            return self.last_feedback_message
        
        # Detect errors above threshold
        detected_errors = []
        for i, prob in enumerate(error_predictions):
            if prob > self.error_threshold:
                detected_errors.append(i)
        
        # No errors detected - provide encouragement
        if not detected_errors:
            feedback = self._get_encouragement()
            self.last_feedback_message = feedback
            self.last_feedback_time = current_time
            return feedback
        
        # Prioritize errors
        detected_errors.sort(key=lambda x: self.ERROR_PRIORITIES[x], reverse=True)
        
        # Get highest priority error
        primary_error = detected_errors[0]
        feedback = self.ERROR_MESSAGES[primary_error]
        
        # Add secondary error if exists
        if len(detected_errors) > 1:
            secondary_error = detected_errors[1]
            feedback += f" | {self.ERROR_MESSAGES[secondary_error]}"
        
        self.last_feedback_message = feedback
        self.last_feedback_time = current_time
        
        return feedback
    
    def _get_encouragement(self) -> str:
        """Get exercise-specific encouragement message"""
        messages = self.ENCOURAGEMENT.get(self.exercise_type, self.ENCOURAGEMENT['squat'])
        message = messages[self.encouragement_index % len(messages)]
        self.encouragement_index += 1
        return message
    
    def set_exercise(self, exercise_type: str):
        """Change exercise type"""
        self.exercise_type = exercise_type
        self.encouragement_index = 0
    
    def reset(self):
        """Reset feedback state"""
        self.last_feedback_time = 0
        self.last_feedback_message = ""
        self.encouragement_index = 0
