# tests/domain/test_progress_model.py
import pytest
from datetime import datetime, date
from pydantic import ValidationError

from domain.progress import ProgressRecord


class TestProgressModel:
    """Тесты для валидации ProgressRecord"""
    
    def test_valid_progress_record(self):
        """Тест создания корректной модели прогресса"""
        # Текущая дата
        today = date.today()
        
        # Создаем корректную запись прогресса
        progress = ProgressRecord(
            user_id="user123",
            date=today,
            score=42,
            correct_answers=8,
            total_answers=10,
            time_spent=120.5
        )
        
        # Проверяем, что поля заполнены правильно
        assert progress.user_id == "user123"
        assert progress.date == today
        assert progress.score == 42
        assert progress.correct_answers == 8
        assert progress.total_answers == 10
        assert progress.time_spent == 120.5
        assert progress.success_rate == 0.8  # 8/10 = 0.8
        
    def test_progress_record_with_zero_answers(self):
        """Тест создания прогресса с нулевым количеством ответов"""
        today = date.today()
        
        progress = ProgressRecord(
            user_id="user123",
            date=today,
            score=0,
            correct_answers=0,
            total_answers=0,
            time_spent=0
        )
        
        # При total_answers=0, success_rate должен быть 0
        assert progress.success_rate == 0
        
    def test_progress_record_negative_values(self):
        """Тест для проверки отрицательных значений"""
        today = date.today()
        
        # Проверяем, что отрицательный score вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            ProgressRecord(
                user_id="user123",
                date=today,
                score=-5,  # Отрицательное значение
                correct_answers=8,
                total_answers=10,
                time_spent=120
            )
            
        errors = error_info.value.errors()
        assert any("score" in error.get("loc", []) for error in errors)
        
        # Проверяем отрицательное количество правильных ответов
        with pytest.raises(ValidationError) as error_info:
            ProgressRecord(
                user_id="user123",
                date=today,
                score=42,
                correct_answers=-1,  # Отрицательное значение
                total_answers=10,
                time_spent=120
            )
            
        errors = error_info.value.errors()
        assert any("correct_answers" in error.get("loc", []) for error in errors)
        
    def test_progress_record_correct_greater_than_total(self):
        """Тест на случай, когда correct_answers > total_answers"""
        today = date.today()
        
        # Создаем запись, где correct_answers > total_answers
        with pytest.raises(ValidationError) as error_info:
            ProgressRecord(
                user_id="user123",
                date=today,
                score=42,
                correct_answers=12,  # Больше, чем total_answers
                total_answers=10,
                time_spent=120
            )
            
        # Проверяем наличие ошибки валидации в Pydantic V2
        errors = error_info.value.errors()
        
        # Печатаем ошибки для отладки
        print(f"Validation errors: {errors}")
        
        # Проверяем содержимое ошибки - ищем либо в loc, либо в msg, либо в type
        error_found = False
        for error in errors:
            # Проверяем есть ли где-то упоминание о количестве ответов
            error_str = str(error)
            if ("correct_answers" in error_str or 
                "total_answers" in error_str or 
                "количество" in error_str.lower()):
                error_found = True
                break
                
        assert error_found, "Ошибка валидации не содержит информации о некорректном количестве ответов"
        
    def test_progress_record_success_rate_calculation(self):
        """Тест расчета success_rate для различных значений"""
        today = date.today()
        
        # Тест 1: 100% успех
        progress = ProgressRecord(
            user_id="user123",
            date=today,
            score=100,
            correct_answers=10,
            total_answers=10,
            time_spent=60
        )
        assert progress.success_rate == 1.0
        
        # Тест 2: 50% успех
        progress = ProgressRecord(
            user_id="user123",
            date=today,
            score=50,
            correct_answers=5,
            total_answers=10,
            time_spent=60
        )
        assert progress.success_rate == 0.5
        
        # Тест 3: 0% успех
        progress = ProgressRecord(
            user_id="user123",
            date=today,
            score=0,
            correct_answers=0,
            total_answers=10,
            time_spent=60
        )
        assert progress.success_rate == 0
