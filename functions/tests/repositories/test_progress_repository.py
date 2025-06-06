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
        
    def test_get_progress(self, progress_repository, firestore_client):
        """Тест получения записей прогресса за указанный период"""
        user_id = "test_user_789"
        today = date.today()
        
        # Создаем тестовые записи за 5 дней
        expected_records = []
        for days_ago in range(5):
            current_date = today - timedelta(days=days_ago)
            score = 20 - days_ago * 2  # Убывающие очки: 20, 18, 16, 14, 12
            correct = 10 - days_ago    # Убывающие правильные ответы: 10, 9, 8, 7, 6
            
            # Записываем прогресс напрямую в Firestore
            doc_id = f"{user_id}_{current_date.isoformat()}"
            data = {
                "user_id": user_id,
                "date": current_date.isoformat(),
                "score": score,
                "correct_answers": correct,
                "total_answers": 10,
                "time_spent": 90.0 + days_ago * 10  # 90, 100, 110, 120, 130
            }
            firestore_client.collection("progress").document(doc_id).set(data)
            
            # Сохраняем ожидаемую запись для сравнения
            expected_records.append(ProgressRecord(
                user_id=user_id,
                date=current_date,
                score=score,
                correct_answers=correct,
                total_answers=10,
                time_spent=90.0 + days_ago * 10
            ))
        
        # Создаем записи для другого пользователя, которые не должны попасть в выборку
        other_user_id = "other_user_123"
        for days_ago in range(5):
            current_date = today - timedelta(days=days_ago)
            firestore_client.collection("progress").document(f"{other_user_id}_{current_date.isoformat()}").set({
                "user_id": other_user_id,
                "date": current_date.isoformat(),
                "score": 5,
                "correct_answers": 3,
                "total_answers": 5,
                "time_spent": 50.0
            })
        
        # Выбираем период для запроса: последние 3 дня
        start_date = (today - timedelta(days=2)).isoformat()
        end_date = today.isoformat()
        
        # Получаем записи за указанный период
        result_records = progress_repository.get_progress(user_id, start_date, end_date)
        
        # Проверяем количество записей
        assert len(result_records) == 3
        
        # Проверяем, что все записи относятся к запрошенному пользователю
        for record in result_records:
            assert record.user_id == user_id
        
        # Проверяем, что все даты находятся в запрошенном диапазоне
        for record in result_records:
            record_date = record.date
            assert record_date >= date.fromisoformat(start_date)
            assert record_date <= date.fromisoformat(end_date)
            
        # Проверяем содержимое записей (должны совпадать с первыми 3 ожидаемыми записями)
        expected_in_range = [rec for rec in expected_records 
                            if rec.date >= date.fromisoformat(start_date) and 
                                rec.date <= date.fromisoformat(end_date)]
        
        # Сортируем записи по дате для корректного сравнения
        expected_in_range.sort(key=lambda x: x.date, reverse=True)
        result_records.sort(key=lambda x: x.date, reverse=True)
        
        # Проверяем содержимое каждой записи
        for i, record in enumerate(result_records):
            expected = expected_in_range[i]
            assert record.user_id == expected.user_id
            assert record.date == expected.date
            assert record.score == expected.score
            assert record.correct_answers == expected.correct_answers
            assert record.total_answers == expected.total_answers
            assert record.time_spent == expected.time_spent
            assert abs(record.success_rate - (record.correct_answers / record.total_answers)) < 0.001
