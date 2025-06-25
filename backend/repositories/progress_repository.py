from domain.progress import ProgressRecord
from datetime import date, datetime
from typing import List
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.async_client import AsyncClient

class ProgressRepository:
    def __init__(self, db: AsyncClient):
        self._collection = db.collection("progress")

    async def record_daily_score(self, record: ProgressRecord) -> None:
        """
        Сохраняет запись ProgressRecord, преобразуя date в строку ISO,
        чтобы Firestore мог сохранить значение.
        """
        # Формируем уникальный ID документа: "<user_id>_<YYYY-MM-DD>"
        doc_id = f"{record.user_id}_{record.date.isoformat()}"
        data = record.model_dump(mode="json")
        # В mode="json" date уже преобразуется в строку автоматически
        await self._collection.document(doc_id).set(data)

    async def sum_total_score(self, user_id: str) -> int:
        """Возвращает сумму всех очков пользователя за всё время."""
        query = self._collection.where(filter=FieldFilter("user_id", "==", user_id))
        total = 0
        async for doc in query.stream():
            data = doc.to_dict()
            total += data.get("score", 0)
        return total

    async def sum_scores_for_week(self, user_id: str, week_ago: datetime) -> int:
        """
        Суммирует daily_score для всех записей, где поле date >= week_ago.date().
        Поскольку мы храним date как строку "YYYY-MM-DD", сравниваем строку.
        """
        # week_ago.date().isoformat() даст "YYYY-MM-DD"
        week_str = week_ago.date().isoformat()
        query = (
            self._collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("date", ">=", week_str))
        )
        total = 0
        async for doc in query.stream():
            data = doc.to_dict()
            total += data.get("score", 0)
        return total
        
    async def get_progress(self, user_id: str, start_date: str, end_date: str) -> List[ProgressRecord]:
        """
        Получает записи прогресса за указанный период.
        
        Args:
            user_id: ID пользователя
            start_date: Начальная дата в формате ISO (YYYY-MM-DD)
            end_date: Конечная дата в формате ISO (YYYY-MM-DD)
            
        Returns:
            Список объектов ProgressRecord
        """
        query = (
            self._collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("date", ">=", start_date))
            .where(filter=FieldFilter("date", "<=", end_date))
        )
        
        progress_records: List[ProgressRecord] = []
        async for doc in query.stream():
            data = doc.to_dict()
            # Конвертируем строку даты обратно в объект date
            if isinstance(data["date"], str):
                data["date"] = date.fromisoformat(data["date"])
            # Создаем объект ProgressRecord из данных Firestore
            progress_records.append(ProgressRecord.model_validate(data))
            
        return progress_records
