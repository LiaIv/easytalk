# functions/tests/test_session_repository.py

import pytest
from datetime import datetime
from domain.session import SessionModel, RoundDetail
from repositories.session_repository import SessionRepository


@pytest.fixture()
def session_repo():
    """
    Фикстура pytest, возвращающая экземпляр SessionRepository,
    которую будет использовать каждый тест.
    """
    return SessionRepository()


def test_create_and_get_session(session_repo):
    """
    1) Создаём SessionModel (без деталей, без ended_at, без score).
    2) Вызываем create_session.
    3) Получаем данные через get_session и проверяем поля.
    """
    # Шаг 1: создаём объект модели
    session = SessionModel(
        session_id="test123",
        user_id="user1",
        game_type="guess_animal",
        started_at=datetime.utcnow()
    )

    # Шаг 2: сохраняем в эмуляторе Firestore
    session_repo.create_session(session)

    # Шаг 3: забираем из Firestore
    fetched = session_repo.get_session("test123")
    assert fetched is not None
    # Проверяем, что поля совпадают
    assert fetched.user_id == "user1"
    assert fetched.game_type == "guess_animal"
    # Поскольку детали, ended_at и score не передавались, они должны быть None
    assert fetched.details is None
    assert fetched.ended_at is None
    assert fetched.score is None


def test_update_and_get_session(session_repo):
    """
    1) Сначала создаём простую сессию
    2) Формируем список RoundDetail (10 объектов)
    3) Вызываем update_session с details, ended_at и score
    4) Проверяем, что при get_session появились новые поля
    """
    session_id = "update_test"
    # Сначала создаём и сохраняем базовую сессию
    base_session = SessionModel(
        session_id=session_id,
        user_id="user2",
        game_type="build_sentence",
        started_at=datetime.utcnow()
    )
    session_repo.create_session(base_session)

    # Формируем 10 объектов RoundDetail
    details = [
        RoundDetail(round_index=i + 1, is_correct=(i % 2 == 0), attempts=1 + i % 3)
        for i in range(10)
    ]
    new_score = 42
    ended_at = datetime.utcnow()

    # Вызываем update_session
    session_repo.update_session(session_id, details, ended_at, new_score)

    # Забираем обновлённую сессию
    fetched = session_repo.get_session(session_id)
    assert fetched is not None
    # Проверяем, что score и ended_at равны переданным
    assert fetched.score == new_score
    # Проверяем, что details длины 10, и хотя бы первый элемент совпадает
    assert isinstance(fetched.details, list)
    assert len(fetched.details) == 10
    assert fetched.details[0].round_index == 1
    assert fetched.details[0].is_correct is True
    assert fetched.details[0].attempts == 1
