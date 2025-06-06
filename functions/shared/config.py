# functions/shared/config.py

import os
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore

# 1) Путь к JSON-файлу сервисного аккаунта Firebase.
#    Если вы установите переменную среды GOOGLE_APPLICATION_CREDENTIALS,
#    то будет использован путь из неё. В противном случае —
#    файл serviceAccountKey.json из этой же папки.
SERVICE_ACCOUNT_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
)

# 2) Инициализация Firebase Admin SDK с проверкой на существование
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)

# Инициализация только если приложение еще не было инициализировано
try:
    # Сначала проверяем, существует ли уже приложение по умолчанию
    default_app = firebase_admin.get_app()
    print("Firebase already initialized, using existing app")
    initialize_app = default_app
except ValueError:
    # Если не существует, инициализируем новое
    print("Initializing Firebase for the first time")
    initialize_app = firebase_admin.initialize_app(cred)

# 3) Получаем клиент Firestore через Admin SDK
firestore_client = admin_firestore.client()
