# functions/repositories/progress_repository.py

from shared.config import firestore_client
from domain.progress import ProgressRecord
from datetime import date, datetime

class ProgressRepository:
    def __init__(self):
        self._collection = firestore_client.collection("progress")

    def record_daily_score(self, record: ProgressRecord) -> None:
        """
        Сохраняет запись ProgressRecord, преобразуя date в строку ISO,
        чтобы Firestore мог сохранить значение.
        """
        # Формируем уникальный ID документа: "<user_id>_<YYYY-MM-DD>"
        doc_id = f"{record.user_id}_{record.date.isoformat()}"
        data = record.dict()
        # Конвертируем поле date (type: date) в строку
        data["date"] = data["date"].isoformat()
        self._collection.document(doc_id).set(data)

    def sum_scores_for_week(self, user_id: str, week_ago: datetime) -> int:
        """
        Суммирует daily_score для всех записей, где поле date >= week_ago.date().
        Поскольку мы храним date как строку "YYYY-MM-DD", сравниваем строку.
        """
        # week_ago.date().isoformat() даст "YYYY-MM-DD"
        week_str = week_ago.date().isoformat()
        query = (
            self._collection
            .where("user_id", "==", user_id)
            .where("date", ">=", week_str)
        )
        total = 0
        for doc in query.stream():
            data = doc.to_dict()
            total += data.get("daily_score", 0)
        return total
