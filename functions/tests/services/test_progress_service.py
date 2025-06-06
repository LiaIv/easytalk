# functions/tests/services/test_progress_service.py

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime, timedelta
from typing import List

from domain.progress import ProgressRecord
from repositories.progress_repository import ProgressRepository
from services.progress_service import ProgressService


class TestProgressService:
    """Тесты для сервиса прогресса пользователя"""

    @pytest.fixture
    def progress_repository_mock(self):
        """Мок для ProgressRepository"""
        mock = Mock(spec=ProgressRepository)
        return mock

    @pytest.fixture
    def progress_service(self, progress_repository_mock):
        """Создание экземпляра сервиса с моком для ProgressRepository"""
        return ProgressService(progress_repo=progress_repository_mock)

    @pytest.fixture
    def sample_record(self):
        """Фикстура для примера записи прогресса"""
        return ProgressRecord(
            user_id="test_user_123",
            date=date.today(),
            score=75,
            correct_answers=15,
            total_answers=20,
            time_spent=150.5
        )

    @pytest.fixture
    def sample_records_list(self):
        """Фикстура для списка записей прогресса за несколько дней"""
        today = date.today()
        records = []
        
        # Создаем записи за последние 5 дней
        for i in range(5):
            record_date = today - timedelta(days=i)
            records.append(ProgressRecord(
                user_id="test_user_123",
                date=record_date,
                score=50 + i * 10,  # 50, 60, 70, 80, 90
                correct_answers=10 + i,  # 10, 11, 12, 13, 14
                total_answers=15 + i,  # 15, 16, 17, 18, 19
                time_spent=100.0 + i * 10  # 100, 110, 120, 130, 140
            ))
        
        return records

    def test_record_progress(self, progress_service, progress_repository_mock):
        """Тест сохранения прогресса пользователя"""
        # Подготовка данных
        user_id = "test_user_123"
        score = 75
        correct_answers = 15
        total_answers = 20
        time_spent = 150.5
        test_date = date(2025, 6, 1)
        
        # Выполняем метод
        progress_id = progress_service.record_progress(
            user_id=user_id,
            score=score,
            correct_answers=correct_answers,
            total_answers=total_answers,
            time_spent=time_spent,
            record_date=test_date
        )
        
        # Проверяем, что метод репозитория вызван с правильными параметрами
        progress_repository_mock.record_daily_score.assert_called_once()
        record = progress_repository_mock.record_daily_score.call_args[0][0]
        
        # Проверяем содержимое записи
        assert isinstance(record, ProgressRecord)
        assert record.user_id == user_id
        assert record.date == test_date
        assert record.score == score
        assert record.correct_answers == correct_answers
        assert record.total_answers == total_answers
        assert record.time_spent == time_spent
        
        # Проверяем возвращаемый ID
        assert progress_id == f"{user_id}_{test_date.isoformat()}"

    def test_record_progress_default_date(self, progress_service, progress_repository_mock):
        """Тест сохранения прогресса пользователя с датой по умолчанию"""
        # Подготовка данных
        user_id = "test_user_123"
        score = 75
        
        # Выполняем метод без указания даты
        with patch('services.progress_service.date') as mock_date:
            today = date(2025, 6, 6)
            mock_date.today.return_value = today
            
            progress_id = progress_service.record_progress(
                user_id=user_id,
                score=score,
                correct_answers=15,
                total_answers=20,
                time_spent=150.5
            )
            
            # Проверяем, что использовалась текущая дата
            mock_date.today.assert_called_once()
            
            # Проверяем возвращаемый ID с текущей датой
            assert progress_id == f"{user_id}_{today.isoformat()}"

    def test_get_progress(self, progress_service, progress_repository_mock, sample_records_list):
        """Тест получения прогресса за период"""
        # Подготовка данных
        user_id = "test_user_123"
        days = 5
        today = date(2025, 6, 6)
        start_date = today - timedelta(days=days-1)
        
        # Настройка мока для возвращения тестовых данных
        progress_repository_mock.get_progress.return_value = sample_records_list
        
        # Патчим метод date.today() для стабильности теста
        with patch('services.progress_service.date') as mock_date:
            mock_date.today.return_value = today
            
            # Выполняем тестируемый метод
            result = progress_service.get_progress(user_id, days)
            
            # Проверяем вызов репозитория с правильными параметрами
            progress_repository_mock.get_progress.assert_called_once()
            args = progress_repository_mock.get_progress.call_args[0]
            assert args[0] == user_id
            assert args[1] == start_date.isoformat()
            assert args[2] == today.isoformat()
            
            # Проверяем структуру и содержимое результата
            assert "data" in result
            assert "total_score" in result
            assert "average_score" in result
            assert "success_rate" in result
            
            # Проверяем данные
            assert len(result["data"]) == 5
            assert result["total_score"] == 350  # 50 + 60 + 70 + 80 + 90
            assert result["average_score"] == 70.0  # 350 / 5
            
            # Вычисляем ожидаемый success_rate
            total_correct = sum(r.correct_answers for r in sample_records_list)
            total_answers = sum(r.total_answers for r in sample_records_list)
            expected_success_rate = round(total_correct / total_answers, 2)
            
            assert result["success_rate"] == expected_success_rate

    def test_get_progress_empty_data(self, progress_service, progress_repository_mock):
        """Тест получения прогресса при отсутствии данных"""
        # Настройка мока для возвращения пустого списка
        progress_repository_mock.get_progress.return_value = []
        
        # Выполняем тестируемый метод
        result = progress_service.get_progress("test_user", 7)
        
        # Проверяем структуру и содержимое результата при отсутствии данных
        assert result["data"] == []
        assert result["total_score"] == 0
        assert result["average_score"] == 0
        assert result["success_rate"] == 0

    def test_get_weekly_summary(self, progress_service, progress_repository_mock):
        """Тест получения суммарных данных за неделю"""
        # Подготовка данных
        user_id = "test_user_123"
        expected_score = 350
        
        # Настройка мока для возвращения ожидаемого значения
        progress_repository_mock.sum_scores_for_week.return_value = expected_score
        
        # Выполняем тестируемый метод
        result = progress_service.get_weekly_summary(user_id)
        
        # Проверяем вызов репозитория
        progress_repository_mock.sum_scores_for_week.assert_called_once()
        args = progress_repository_mock.sum_scores_for_week.call_args[0]
        assert args[0] == user_id
        assert isinstance(args[1], datetime)  # week_ago
        
        # Проверяем результат
        assert result == expected_score
