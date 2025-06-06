# functions/tests/repositories/test_progress_repository.py

import pytest
from datetime import date, datetime, timedelta
from domain.progress import ProgressRecord
from repositories.progress_repository import ProgressRepository


class TestProgressRepository:
    """Тесты для репозитория прогресса пользователей"""

    @pytest.fixture
    def progress_repository(self):
        """Инициализируем репозиторий для тестов"""
        return ProgressRepository()

    @pytest.fixture
    def sample_progress_record(self):
        """Фикстура с примером записи прогресса"""
        return ProgressRecord(
            user_id="test_user_123",
            date=date(2025, 6, 6),
            score=10,
            correct_answers=7,
            total_answers=10,
            time_spent=120.5  # 2 минуты 30 секунд
        )

    def test_record_daily_score(self, progress_repository, sample_progress_record, firestore_client):
        """Тест записи дневного прогресса пользователя"""
        # Записываем прогресс
        progress_repository.record_daily_score(sample_progress_record)

        # Формируем ID документа как в репозитории
        doc_id = f"{sample_progress_record.user_id}_{sample_progress_record.date.isoformat()}"
        
        # Проверяем, что запись создана в Firestore
        doc = firestore_client.collection("progress").document(doc_id).get()
        assert doc.exists
        
        # Проверяем данные в записи
        progress_data = doc.to_dict()
        assert progress_data["user_id"] == sample_progress_record.user_id
        assert progress_data["date"] == sample_progress_record.date.isoformat()  # Дата сохраняется как ISO строка
        assert progress_data["score"] == sample_progress_record.score
        assert progress_data["correct_answers"] == sample_progress_record.correct_answers
        assert progress_data["total_answers"] == sample_progress_record.total_answers
        assert progress_data["time_spent"] == sample_progress_record.time_spent

    def test_sum_scores_for_week(self, progress_repository, firestore_client):
        """Тест подсчета суммы баллов за неделю"""
        user_id = "test_user_456"
        today = date.today()
        
        # Создаем записи за последние 10 дней
        for days_ago in range(10):
            current_date = today - timedelta(days=days_ago)
            score = 10 - days_ago  # Чем дальше в прошлое, тем меньше очков
            
            # Записываем прогресс напрямую в Firestore (имитируем существующие записи)
            doc_id = f"{user_id}_{current_date.isoformat()}"
            data = {
                "user_id": user_id,
                "date": current_date.isoformat(),
                "score": score,
                "correct_answers": 5,
                "total_answers": 10,
                "time_spent": 100.0
            }
            firestore_client.collection("progress").document(doc_id).set(data)
        
        # Получаем сумму баллов за неделю (7 дней)
        week_ago = datetime.combine(today - timedelta(days=6), datetime.min.time())
        total = progress_repository.sum_scores_for_week(user_id, week_ago)
        
        # Проверяем результат: сумма баллов за последние 7 дней
        # 10 + 9 + 8 + 7 + 6 + 5 + 4 = 49
        expected_total = sum(range(4, 11))
        assert total == expected_total
