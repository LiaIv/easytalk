from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """Value object representing a score in a game."""
    
    value: int
    max_possible: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Score cannot be negative")
        
        if self.max_possible < 0:
            raise ValueError("Maximum possible score cannot be negative")
        
        if self.value > self.max_possible:
            raise ValueError("Score cannot exceed maximum possible score")
    
    @property
    def percentage(self) -> float:
        """Calculate the percentage score."""
        if self.max_possible == 0:
            return 0.0
        return (self.value / self.max_possible) * 100
