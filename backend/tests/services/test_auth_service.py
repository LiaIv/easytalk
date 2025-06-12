# backend/tests/services/test_auth_service.py

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from domain.user import UserModel
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from google.cloud.firestore import Client


class TestAuthService:
    """Тесты для сервиса аутентификации"""

    @pytest.fixture
    def db_mock(self):
        """Мок для Firestore Client"""
        return Mock(spec=Client)

    @pytest.fixture
    def user_repository_mock(self):
        """Мок для UserRepository. Используется для проверки вызовов к нему."""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def auth_service(self, db_mock, user_repository_mock):
        """Создание экземпляра сервиса с моком для db и UserRepository."""
        # Патчим UserRepository в модуле, где он используется AuthService
        with patch('services.auth_service.UserRepository', return_value=user_repository_mock):
            service = AuthService(db=db_mock)
            return service

    @patch('firebase_admin.auth.create_user')
    def test_register_user(self, mock_create_user, auth_service, user_repository_mock):
        """Тест регистрации нового пользователя"""
        # Подготовка тестовых данных
        email = "test@example.com"
        password = "test_password"
        display_name = "Test User"
        level = "beginner"
        
        # Мок для Firebase Auth create_user
        user_record = MagicMock()
        user_record.uid = "firebase_uid_123"
        mock_create_user.return_value = user_record
        
        # Вызываем тестируемый метод
        user = auth_service.register_user(email, password, display_name, level)
        
        # Проверяем, что Firebase Auth был вызван с правильными параметрами
        mock_create_user.assert_called_once_with(
            email=email,
            password=password,
            display_name=display_name
        )
        
        # Проверяем, что репозиторий был вызван для сохранения пользователя
        user_repository_mock.create_user.assert_called_once()
        
        # Проверяем, что пользователь создан с правильными данными
        assert user.uid == user_record.uid
        assert user.email == email
        assert user.display_name == display_name
        assert user.photo_url is None  # В UserModel используется photo_url, а не avatar_url
        assert user.level == level
        assert isinstance(user.created_at, datetime)

    @patch('firebase_admin.auth.verify_id_token')
    @patch('os.environ.get')
    def test_verify_token_normal_mode(self, mock_env_get, mock_verify_token, auth_service):
        """Тест верификации токена в обычном режиме (не debug)"""
        # Настройка окружения - не debug
        mock_env_get.return_value = 'False'
        
        # Мок для Firebase Auth verify_id_token
        token = "valid_token_123"
        decoded_token = {"uid": "firebase_uid_123"}
        mock_verify_token.return_value = decoded_token
        
        # Вызываем тестируемый метод
        uid = auth_service.verify_token(token)
        
        # Проверяем, что Firebase Auth был вызван с токеном
        mock_verify_token.assert_called_once_with(token)
        
        # Проверяем, что вернулся правильный UID
        assert uid == decoded_token["uid"]

    @patch('firebase_admin.auth.verify_id_token')
    @patch('os.environ.get')
    def test_verify_token_debug_mode_with_token(self, mock_env_get, mock_verify_token, auth_service):
        """Тест верификации токена в режиме debug с переданным токеном"""
        # Настройка окружения - debug
        mock_env_get.return_value = 'True'
        
        # Вызываем тестируемый метод
        token = "debug_token_123"
        uid = auth_service.verify_token(token)
        
        # Проверяем, что Firebase Auth НЕ был вызван
        mock_verify_token.assert_not_called()
        
        # Проверяем, что возвращен тот же токен
        assert uid == token

    @patch('firebase_admin.auth.verify_id_token')
    @patch('os.environ.get')
    def test_verify_token_debug_mode_without_token(self, mock_env_get, mock_verify_token, auth_service):
        """Тест верификации токена в режиме debug без токена"""
        # Настройка окружения - debug
        mock_env_get.return_value = 'True'
        
        # Вызываем тестируемый метод с пустым токеном
        uid = auth_service.verify_token(None)
        
        # Проверяем, что Firebase Auth НЕ был вызван
        mock_verify_token.assert_not_called()
        
        # Проверяем, что возвращен тестовый ID
        assert uid == 'test_user_id'

    @patch('firebase_admin.auth.verify_id_token')
    @patch('os.environ.get')
    def test_verify_token_error(self, mock_env_get, mock_verify_token, auth_service):
        """Тест обработки ошибки при верификации токена"""
        # Настройка окружения - не debug
        mock_env_get.return_value = 'False'
        
        # Настраиваем мок, чтобы он вызвал исключение
        token = "invalid_token"
        mock_verify_token.side_effect = Exception("Token verification failed")
        
        # Проверяем, что метод выбрасывает исключение
        with pytest.raises(Exception) as e:
            auth_service.verify_token(token)
            
        # Проверяем сообщение об ошибке
        assert "Token verification failed" in str(e)
