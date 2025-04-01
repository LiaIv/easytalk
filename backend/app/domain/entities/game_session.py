from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class GameSession:
    """GameSession entity representing a single learning session/game play."""
    
    user_id: UUID
    game_type: str  # e.g., "vocabulary", "grammar", "listening"
    difficulty_level: str  # e.g., "beginner", "intermediate", "advanced"
    id: UUID = field(default_factory=uuid4)
    started_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    updated_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    completed_at: Optional[datetime] = None
    score: int = 0
    max_score: int = 0
    correct_answers: int = 0
    total_questions: int = 0
    experience_earned: int = 0
    
    def complete(self, score: int, correct_answers: int, total_questions: int):
        """Mark the game session as completed with results."""
        self.completed_at = datetime.utcnow()
        self.score = score
        self.correct_answers = correct_answers
        self.total_questions = total_questions
        
        # Calculate experience points based on difficulty and performance
        # This is a simple calculation, can be adjusted based on game mechanics
        difficulty_multiplier = {
            "beginner": 1,
            "intermediate": 1.5,
            "advanced": 2
        }.get(self.difficulty_level.lower(), 1)
        
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        self.experience_earned = int(score * difficulty_multiplier * (1 + accuracy))
        
        return self.experience_earned
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """Calculate the duration of the game session in seconds."""
        if not self.completed_at:
            return None
        return int((self.completed_at - self.started_at).total_seconds())
    
    @property
    def accuracy_percentage(self) -> float:
        """Calculate the accuracy percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
