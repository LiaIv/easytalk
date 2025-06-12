from datetime import date
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from domain.achievement import AchievementModel, AchievementType


class AchievementRepository:
    def __init__(self, db: AsyncClient):
        self._collection = db.collection("achievements")

    async def create_achievement(self, achievement: AchievementModel) -> None:
        """
        Сохраняем AchievementModel в Firestore. С помощью mode="json" 
        все типы date и datetime будут автоматически преобразованы в строки JSON.
        """
        data = achievement.model_dump(mode="json")
        await self._collection.document(achievement.achievement_id).set(data)

    async def get_user_achievements(self, user_id: str) -> list[AchievementModel]:
        docs_stream = self._collection.where(filter=FieldFilter("user_id", "==", user_id)).stream()
        results = []
        async for doc in docs_stream:
            obj = doc.to_dict()
            if ps := obj.get("period_start_date"):
                obj["period_start_date"] = date.fromisoformat(ps)
            results.append(AchievementModel(**obj))
        return results

    async def exists_weekly_achievement(self, user_id: str, period_start: date) -> bool:
        period_str = period_start.isoformat()
        docs_stream = (
            self._collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("type", "==", AchievementType.WEEKLY_FIFTY.value))
            .where(filter=FieldFilter("period_start_date", "==", period_str))
            .limit(1)
            .stream()
        )
        async for _ in docs_stream:
            return True
        return False

    async def delete_weekly_achievements(self, user_id: str, period_start: date) -> None:
        period_str = period_start.isoformat()
        docs_to_delete_stream = (
            self._collection
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("type", "==", AchievementType.WEEKLY_FIFTY.value))
            .where(filter=FieldFilter("period_start_date", "==", period_str))
            .stream()
        )
        
        async for doc in docs_to_delete_stream:
            await doc.reference.delete()


