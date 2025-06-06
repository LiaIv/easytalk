# backend/domain/progress.py

from pydantic import BaseModel, conint, Field, computed_field, model_validator
from datetime import date
from typing import ClassVar

class ProgressRecord(BaseModel):
    user_id: str
    date: date
    score: conint(ge=0)
    correct_answers: conint(ge=0)
    total_answers: conint(ge=0)
    time_spent: float = Field(ge=0.0)  # Время в секундах
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
    
    # Вычисляемое поле для success_rate
    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on correct_answers and total_answers"""
        if self.total_answers > 0:
            return self.correct_answers / self.total_answers
        return 0.0

    # Проверка полей до инициализации модели
    @model_validator(mode='before')
    @classmethod
    def validate_answers(cls, data):
        """Проверяем, что correct_answers <= total_answers"""
        if isinstance(data, dict):
            correct = data.get('correct_answers', 0)
            total = data.get('total_answers', 0)
            if correct > total:
                # Вызываем ошибку с правильным указанием поля
                raise ValueError({
                    'loc': ('correct_answers',),
                    'msg': 'Количество правильных ответов не может быть больше общего количества ответов',
                    'type': 'value_error'
                })
        return data
