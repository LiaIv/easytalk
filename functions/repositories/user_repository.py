# functions/repositories/user_repository.py

from shared.config import firestore_client
from domain.user import UserModel

class UserRepository:
    def __init__(self):
        self._collection = firestore_client.collection("users")

    def create_user(self, user: UserModel) -> None:
        self._collection.document(user.uid).set(user.dict())

    def get_user(self, uid: str) -> UserModel | None:
        doc = self._collection.document(uid).get()
        if doc.exists:
            return UserModel(**doc.to_dict())
        return None

    def update_user(self, user: UserModel) -> None:
        data = user.dict(exclude={"created_at"})
        self._collection.document(user.uid).update(data)

    def delete_user(self, uid: str) -> None:
        self._collection.document(uid).delete()
