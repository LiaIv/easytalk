# functions/repositories/achievement_repository.py

from shared.config import firestore_client
from domain.achievement import AchievementModel
from datetime import date
from typing import Optional

class AchievementRepository:
    def __init__(self):
        self._collection = firestore_client.collection("achievements")

    def create_achievement(self, achievement: AchievementModel) -> None:
        """
        Сохраняем AchievementModel в Firestore. С помощью mode="json" 
        все типы date и datetime будут автоматически преобразованы в строки JSON.
        """
        data = achievement.model_dump(mode="json")
        # Идентификатор документа — achievement_id
        self._collection.document(achievement.achievement_id).set(data)

    def get_user_achievements(self, user_id: str) -> list[AchievementModel]:
        docs = self._collection.where("user_id", "==", user_id).stream()
        results = []
        for doc in docs:
            obj = doc.to_dict()
            # Если period_start_date хранится как строка, преобразуем её обратно в date
            ps = obj.get("period_start_date")
            if ps is not None:
                # Напомним: Pydantic-модель AchievementModel ожидает `period_start_date` как date | None
                obj["period_start_date"] = date.fromisoformat(ps)
            results.append(AchievementModel(**obj))
        return results

    def exists_weekly_achievement(self, user_id: str, period_start: date) -> bool:
        # Firestore хранит period_start_date в виде строки, поэтому сравним со строковым ISO
        period_str = period_start.isoformat()
        docs = (
            self._collection
            .where("user_id", "==", user_id)
            .where("type", "==", "weekly_fifty")
            .where("period_start_date", "==", period_str)
            .stream()
        )
        return any(True for _ in docs)

    def delete_weekly_achievements(self, user_id: str, period_start: date) -> None:
        """
        Удаляет еженедельные достижения (weekly_fifty) для указанного пользователя и периода.
        """
        period_str = period_start.isoformat()
        docs_query = (
            self._collection
            .where("user_id", "==", user_id)
            .where("type", "==", "weekly_fifty")
            .where("period_start_date", "==", period_str)
        )
        
        docs_to_delete = list(docs_query.stream())
        
        for doc in docs_to_delete:
            doc.reference.delete()
