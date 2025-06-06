# functions/tests/repositories/test_progress_repository.py

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock
from functions.domain.progress import ProgressRecord
from functions.repositories.progress_repository import ProgressRepository


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

    def test_sum_scores_for_week(self, progress_repository, monkeypatch):
        """Тест суммирования очков за неделю с использованием моков"""
        user_id = "test_user_456"
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # Текущий день + 6 дней ранее = 7 дней
        
        # Создаем данные для моков
        mock_scores = []
        for days_ago in range(7):
            current_date = end_date - timedelta(days=days_ago)
            score = days_ago + 4  # Скоры: 4, 5, 6, 7, 8, 9, 10
            
            # Создаем запись для моделирования
            mock_scores.append({
                "user_id": user_id,
                "date": current_date.isoformat(),
                "score": score,
                "correct_answers": 5,
                "total_answers": 10,
                "time_spent": 60.0
            })
        
        # Создаем и настраиваем моки для Firestore
        collection_mock = MagicMock(name="collection_mock")
        where1_mock = MagicMock(name="where1_mock")
        where2_mock = MagicMock(name="where2_mock")
        query_mock = MagicMock(name="query_mock")
        stream_mock = MagicMock(name="stream_mock")
        
        # Связывание цепочки вызовов
        monkeypatch.setattr(progress_repository, "_collection", collection_mock)
        collection_mock.where.return_value = where1_mock
        where1_mock.where.return_value = where2_mock
        where2_mock.stream = stream_mock
        
        # Создаем моки документов
        doc_mocks = []
        for record in mock_scores:
            doc_mock = MagicMock()
            doc_mock.to_dict.return_value = record
            doc_mocks.append(doc_mock)
        
        # Синхронный генератор документов
        def mock_documents_generator():
            for doc in doc_mocks:
                yield doc
                
        # Настройка stream() для возврата генератора документов
        stream_mock.return_value = mock_documents_generator()
        
        # Вызываем тестируемый метод
        # Преобразуем дату в объект datetime, как того ожидает метод
        end_datetime = datetime.combine(end_date, datetime.min.time())
        total = progress_repository.sum_scores_for_week(user_id, end_datetime)
        
        # Проверяем сумму: 4 + 5 + 6 + 7 + 8 + 9 + 10 = 49
        expected_total = sum(range(4, 11))
        assert total == expected_total

        
    def test_get_progress(self, progress_repository, monkeypatch):
        """Тест получения записей прогресса за указанный период с использованием моков"""
        user_id = "test_user_789"
        today = date.today()
        
        # Создаем тестовые данные для моделирования
        expected_records = []
        for days_ago in range(3):  # Только за последние 3 дня, так как это будет в результате запроса
            current_date = today - timedelta(days=days_ago)
            score = 20 - days_ago * 2  # Убывающие очки: 20, 18, 16
            correct = 10 - days_ago    # Убывающие правильные ответы: 10, 9, 8
            
            # Создаем ожидаемую запись
            expected_records.append(ProgressRecord(
                user_id=user_id,
                date=current_date,
                score=score,
                correct_answers=correct,
                total_answers=10,
                time_spent=90.0 + days_ago * 10  # 90, 100, 110
            ))
        
        # Создаем и настраиваем моки для Firestore
        # Инициализация моков для цепочки вызовов Firestore
        collection_mock = MagicMock(name="collection_mock")
        where1_mock = MagicMock(name="where1_mock")
        where2_mock = MagicMock(name="where2_mock")
        query_mock = MagicMock(name="query_mock")
        stream_mock = MagicMock(name="stream_mock")
        
        # Связывание цепочки вызовов
        monkeypatch.setattr(progress_repository, "_collection", collection_mock)
        collection_mock.where.return_value = where1_mock
        where1_mock.where.return_value = where2_mock
        where2_mock.where.return_value = query_mock
        query_mock.stream = stream_mock
        
        # Создаем моки документов для возврата из stream()
        doc_mocks = []
        for record in expected_records:
            doc_mock = MagicMock()
            # to_dict вернет словарь с данными ProgressRecord
            doc_dict = record.model_dump()
            # Преобразуем date в строку, как это делает Firestore
            doc_dict["date"] = doc_dict["date"].isoformat()
            doc_mock.to_dict.return_value = doc_dict
            doc_mocks.append(doc_mock)
        
        # Сделаем синхронный генератор для возврата документов
        def mock_documents_generator():
            for doc in doc_mocks:
                yield doc
                
        # Настройка stream() для возврата генератора документов
        stream_mock.return_value = mock_documents_generator()
        
        # Выбираем период для запроса: последние 3 дня
        start_date = (today - timedelta(days=2)).isoformat()
        end_date = today.isoformat()
        
        # Вызываем тестируемый метод
        result_records = progress_repository.get_progress(user_id, start_date, end_date)
        
        # Проверяем количество записей
        assert len(result_records) == 3
        
        # Проверяем содержимое записей
        for i, record in enumerate(result_records):
            assert record.user_id == expected_records[i].user_id
            assert record.date == expected_records[i].date
            assert record.score == expected_records[i].score
            assert record.correct_answers == expected_records[i].correct_answers
            assert record.total_answers == expected_records[i].total_answers
            assert record.time_spent == expected_records[i].time_spent
        
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
