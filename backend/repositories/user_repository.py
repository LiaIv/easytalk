# backend/repositories/user_repository.py


from domain.user import UserModel

class UserRepository:
    def __init__(self, db):
        self._collection = db.collection("users")

    def create_user(self, user: UserModel) -> None:
        # Используем model_dump с параметром mode="json", который превращает объекты в JSON-совместимые значения
        self._collection.document(user.uid).set(user.model_dump(mode="json"))

    def get_user(self, uid: str) -> UserModel | None:
        doc = self._collection.document(uid).get()
        if doc.exists:
            return UserModel(**doc.to_dict())
        return None

    def update_user(self, user: UserModel) -> None:
        # Исключаем created_at из обновления и преобразуем в JSON-совместимый формат
        data = user.model_dump(mode="json", exclude={"created_at"})
        self._collection.document(user.uid).update(data)

    def delete_user(self, uid: str) -> None:
        self._collection.document(uid).delete()
