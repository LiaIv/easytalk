from domain.session import SessionModel, RoundDetail, SessionStatus
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.async_batch import AsyncWriteBatch
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import List
from datetime import datetime


class SessionRepository:
    def __init__(self, db: AsyncClient):
        # Клиент Firestore передается через конструктор
        self._db = db  # Сохраняем клиент в self._db для использования в других методах
        self._collection = self._db.collection("sessions")

    async def create_session(self, session: SessionModel) -> None:
        """
        Создаёт новый документ sessions/{session_id} с полями:
        - user_id
        - game_type
        - started_at
        (поле session_id используем только как ID документа, но не записываем его в сам документ)
        """
        # Берём словарь из pydantic-модели,
        # но явно исключаем session_id, end_time, score и details,
        # чтобы в Firestore хранились только user_id, game_type, start_time, status
        data = session.model_dump(
            mode="json", exclude={"session_id", "end_time", "score", "details"}
        )
        await self._collection.document(session.session_id).set(data)

    async def update_session(
        self,
        session_id: str,
        details: List[RoundDetail],
        ended_at: datetime,
        score: int,
    ) -> None:
        """
        Обновляет документ sessions/{session_id}:
        - добавляет поле details (список из RoundDetail),
        - добавляет поля ended_at и score.
        Всё в атомарном WriteBatch.
        """
        # Используем self._db для создания batch
        batch: AsyncWriteBatch = self._db.batch()
        doc_ref = self._collection.document(session_id)
        batch.update(
            doc_ref,
            {
                "details": [d.model_dump(mode="json") for d in details],
                "ended_at": ended_at.isoformat(),  # Преобразуем datetime в ISO строку
                "score": score,
                "status": SessionStatus.FINISHED.value,
            },
        )
        await batch.commit()

    async def get_session(self, session_id: str) -> SessionModel | None:
        """
        Получает документ sessions/{session_id} из Firestore и возвращает SessionModel.
        Если документа нет – возвращает None.
        """
        doc = await self._collection.document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            # В полученных данных уже нет session_id, поэтому передаём его отдельно
            return SessionModel(**data, session_id=session_id)
        return None

    async def get_active_session_for_user(self, user_id: str) -> SessionModel | None:
        """Возвращает активную сессию пользователя или None."""
        query = (
            self._collection.where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("status", "==", SessionStatus.ACTIVE.value))
            .limit(1)
        )
        async for doc in query.stream():
            data = doc.to_dict()
            return SessionModel(**data, session_id=doc.id)
        return None
