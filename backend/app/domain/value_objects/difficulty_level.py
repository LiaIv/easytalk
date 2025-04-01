from enum import Enum


class DifficultyLevel(str, Enum):
    """Enum representing different difficulty levels in the game."""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    
    @classmethod
    def get_experience_multiplier(cls, level) -> float:
        """Return experience multiplier based on difficulty level."""
        multipliers = {
            cls.BEGINNER: 1.0,
            cls.INTERMEDIATE: 1.5,
            cls.ADVANCED: 2.0
        }
        return multipliers.get(level, 1.0)
