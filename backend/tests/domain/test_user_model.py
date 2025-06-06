# tests/domain/test_user_model.py
import pytest
from pydantic import ValidationError

# Импортируем тестируемую модель
from domain.user import UserModel


class TestUserModel:
    """Тесты для валидации UserModel"""

    def test_valid_user_model(self):
        """Тест создания корректной модели пользователя"""
        # Создаем полностью заполненный объект
        user = UserModel(
            uid="test123",
            email="test@example.com",
            display_name="Test User",
            photo_url="https://example.com/photo.jpg"
        )
        
        # Проверяем, что поля заполнены правильно
        assert user.uid == "test123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        # В Pydantic V2 URL преобразуются в объекты HttpUrl
        assert str(user.photo_url) == "https://example.com/photo.jpg"

    def test_user_model_optional_fields(self):
        """Тест создания модели пользователя с опциональными полями"""
        # Создаем объект только с обязательными полями
        user = UserModel(
            uid="test123",
            email="test@example.com"
        )
        
        # Проверяем, что обязательные поля заполнены правильно
        assert user.uid == "test123"
        assert user.email == "test@example.com"
        
        # Проверяем, что опциональные поля равны None
        assert user.display_name is None
        assert user.photo_url is None

    def test_user_model_invalid_email(self):
        """Тест для проверки валидации email"""
        # Проверяем, что создание с неверным email вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            UserModel(
                uid="test123",
                email="invalid-email"  # Неверный формат email
            )
        
        # Убеждаемся, что причина ошибки связана с валидацией email
        errors = error_info.value.errors()
        assert any("email" in error.get("loc", []) for error in errors)
        assert any("value is not a valid email address" in error.get("msg", "") for error in errors)

    def test_user_model_invalid_photo_url(self):
        """Тест для проверки валидации URL фото"""
        # Проверяем, что создание с неверным URL фото вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            UserModel(
                uid="test123",
                email="test@example.com",
                photo_url="invalid-url"  # Неверный формат URL
            )
        
        # Убеждаемся, что причина ошибки связана с валидацией URL
        errors = error_info.value.errors()
        assert any("photo_url" in error.get("loc", []) for error in errors)
        assert any("url" in error.get("type", "") for error in errors)

    def test_user_model_missing_required_fields(self):
        """Тест для проверки обязательных полей"""
        # Проверяем, что создание без uid вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            UserModel(
                email="test@example.com"
            )
        
        # Убеждаемся, что причина ошибки связана с отсутствием uid
        errors = error_info.value.errors()
        assert any("uid" in str(error.get("loc", [])) for error in errors)
        # В Pydantic V2 сообщение об ошибке может содержать "missing" вместо "field required"
        assert any("missing" in error.get("type", "").lower() or
                "required" in error.get("msg", "").lower() 
                for error in errors)
