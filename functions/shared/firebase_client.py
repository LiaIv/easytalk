# functions/shared/firebase_client.py

import os
from firebase_admin import initialize_app, credentials, firestore
from firebase_admin import firestore as firestore_admin
import firebase_admin
from typing import Optional

# Одиночный экземпляр Firebase app
_firebase_app: Optional[firebase_admin.App] = None
_db: Optional[firestore.Client] = None


def initialize_firebase() -> firebase_admin.App:
    """
    Инициализирует Firebase Admin SDK, если он еще не инициализирован.
    
    Возвращает:
        firebase_admin.App: Инициализированное Firebase приложение
    """
    global _firebase_app
    
    # Проверяем, инициализирован ли уже Firebase
    if _firebase_app:
        return _firebase_app
    
    # Проверяем, нет ли уже инициализированных приложений Firebase
    try:
        # Пробуем получить уже имеющееся приложение Firebase
        existing_app = firebase_admin.get_app()
        _firebase_app = existing_app
        print("Firebase already initialized, using existing app")
        return existing_app
    except ValueError:
        # Нет существующего приложения, продолжаем инициализацию
        pass
    
    # Проверяем переменные среды для эмуляторов Firebase
    firestore_emulator = os.environ.get('FIRESTORE_EMULATOR_HOST')
    auth_emulator = os.environ.get('FIREBASE_AUTH_EMULATOR_HOST')
    
    # Если эмуляторы в использовании, выводим сообщение
    if firestore_emulator:
        print(f"Using Firestore Emulator: {firestore_emulator}")
    if auth_emulator:
        print(f"Using Firebase Auth Emulator: {auth_emulator}")
    
    # Путь к service account key
    service_account_path = os.environ.get(
        'GOOGLE_APPLICATION_CREDENTIALS',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared', 'serviceAccountKey.json')
    )
    
    try:
        # Проверяем наличие файла credentials
        if os.path.exists(service_account_path):
            # Инициализируем с учетными данными
            cred = credentials.Certificate(service_account_path)
            _firebase_app = initialize_app(cred)
        else:
            # Инициализируем без учетных данных (для локальных эмуляторов или Cloud Functions)
            _firebase_app = initialize_app()
        print("Firebase initialized successfully")
    except ValueError as e:
        # Если Firebase уже инициализирован, получаем существующее приложение
        print(f"Firebase initialization error: {e}")
        _firebase_app = firebase_admin.get_app()
        print("Using existing Firebase app")
    
    return _firebase_app


def get_firestore() -> firestore.Client:
    """
    Возвращает клиент Firestore, инициализируя его при необходимости.
    
    Возвращает:
        firestore.Client: Клиент Firestore для работы с базой данных
    """
    global _db
    
    if not _db:
        # Убеждаемся, что Firebase инициализирован
        initialize_firebase()
        # Создаем клиент Firestore
        _db = firestore_admin.client()
    
    return _db
