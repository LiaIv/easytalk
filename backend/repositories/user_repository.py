from domain.user import UserModel
from google.cloud.firestore_v1.async_client import AsyncClient

class UserRepository:
    def __init__(self, db: AsyncClient):
        self._collection = db.collection("users")

    async def create_user(self, user: UserModel) -> None:
        # Используем model_dump с параметром mode="json", который превращает объекты в JSON-совместимые значения
        await self._collection.document(user.uid).set(user.model_dump(mode="json"))

    async def get_user(self, uid: str) -> UserModel | None:
        doc = await self._collection.document(uid).get()
        if doc.exists:
            return UserModel(**doc.to_dict())
        return None

    async def update_user(self, user: UserModel) -> None:
        # Исключаем created_at из обновления и преобразуем в JSON-совместимый формат
        data = user.model_dump(mode="json", exclude={"created_at"})
        await self._collection.document(user.uid).update(data)

    async def delete_user(self, uid: str) -> None:
        await self._collection.document(uid).delete()
