from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Achievement:
    """Achievement entity representing a user accomplishment."""
    
    name: str
    description: str
    icon_url: str
    experience_reward: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Achievement criteria
    required_level: Optional[int] = None
    required_games: Optional[int] = None
    required_score: Optional[int] = None
    required_accuracy: Optional[float] = None  # as percentage
    
    def check_eligibility(self, user_level: int, games_played: int, 
                         highest_score: int, avg_accuracy: float) -> bool:
        """
        Check if user is eligible for this achievement based on their stats.
        Returns True if eligible, False otherwise.
        """
        eligible = True
        
        if self.required_level is not None and user_level < self.required_level:
            eligible = False
            
        if self.required_games is not None and games_played < self.required_games:
            eligible = False
            
        if self.required_score is not None and highest_score < self.required_score:
            eligible = False
            
        if self.required_accuracy is not None and avg_accuracy < self.required_accuracy:
            eligible = False
            
        return eligible
