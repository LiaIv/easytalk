# backend/tests/repositories/test_user_repository.py

import pytest
from datetime import datetime
from domain.user import UserModel
from repositories.user_repository import UserRepository
from unittest.mock import AsyncMock, MagicMock

class TestUserRepository:
    """Тесты для UserRepository"""
    
    @pytest.fixture
    def user_repository(self, clean_firestore_async):
        """Фикстура создания репозитория пользователей с тестовым клиентом Firestore"""
        return UserRepository(db=clean_firestore_async)
    
    @pytest.fixture
    def sample_user(self):
        """Фикстура создания тестового пользователя"""
        return UserModel(
            uid="test_user_123",
            email="test@example.com",
            display_name="Test User",
            photo_url="https://example.com/photo.jpg",
            level="beginner",
            created_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository, sample_user, clean_firestore_async):
        """Тест создания пользователя в БД"""
        # Создаем пользователя
        await user_repository.create_user(sample_user)
        
        # Проверяем, что пользователь был создан в Firestore
        doc = await clean_firestore_async.collection("users").document(sample_user.uid).get()
        assert doc.exists
        user_data = doc.to_dict()
        assert user_data["uid"] == sample_user.uid
        assert user_data["email"] == sample_user.email
        assert user_data["display_name"] == sample_user.display_name
        # HttpUrl сериализуется как строка
        assert user_data["photo_url"] == str(sample_user.photo_url)
        
    @pytest.mark.asyncio
    async def test_get_user(self, user_repository, sample_user, clean_firestore_async):
        """Тест получения пользователя по ID"""
        # Создаем пользователя для теста
        await clean_firestore_async.collection("users").document(sample_user.uid).set(
            sample_user.model_dump(mode="json")
        )
        
        # Получаем пользователя
        retrieved_user = await user_repository.get_user(sample_user.uid)
        
        # Проверяем полученного пользователя
        assert retrieved_user is not None
        assert retrieved_user.uid == sample_user.uid
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.display_name == sample_user.display_name
        
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_repository):
        """Тест получения несуществующего пользователя"""
        non_existent_user = await user_repository.get_user("non_existent_uid")
        assert non_existent_user is None
        
    @pytest.mark.asyncio
    async def test_update_user(self, user_repository, sample_user, clean_firestore_async):
        """Тест обновления пользователя"""
        # Создаем пользователя для теста
        await clean_firestore_async.collection("users").document(sample_user.uid).set(
            sample_user.model_dump(mode="json")
        )
        
        # Обновляем пользователя
        updated_user = UserModel(
            uid=sample_user.uid,
            email=sample_user.email,
            display_name="Updated Name",  # Изменяем имя
            photo_url=sample_user.photo_url,
            level="intermediate",  # Изменяем уровень
            created_at=sample_user.created_at  # created_at не должен обновиться
        )
        
        await user_repository.update_user(updated_user)
        
        # Получаем пользователя из БД и проверяем обновления
        doc = await clean_firestore_async.collection("users").document(sample_user.uid).get()
        assert doc.exists
        user_data = doc.to_dict()
        assert user_data["display_name"] == "Updated Name"
        assert user_data["level"] == "intermediate"
        
    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository, sample_user, clean_firestore_async):
        """Тест удаления пользователя"""
        # Создаем пользователя для теста
        await clean_firestore_async.collection("users").document(sample_user.uid).set(
            sample_user.model_dump(mode="json")
        )
        
        # Проверяем, что пользователь существует
        doc = await clean_firestore_async.collection("users").document(sample_user.uid).get()
        assert doc.exists
        
        # Удаляем пользователя
        await user_repository.delete_user(sample_user.uid)
        
        # Проверяем, что пользователь был удален
        doc = await clean_firestore_async.collection("users").document(sample_user.uid).get()
        assert not doc.exists
