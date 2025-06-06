# functions/main.py
from flask import Flask, jsonify

# Импорт сервисов и репозиториев для централизованной инициализации
from services.auth_service import AuthService
from services.session_service import SessionService
from repositories.session_repository import SessionRepository
from repositories.achievement_repository import AchievementRepository

# Импорт фабрики Blueprint из вашего роутера
from routers.session_router import create_session_blueprint

app = Flask(__name__)

# --- Инициализация зависимостей --- 
# Создаем экземпляры сервисов и репозиториев один раз
auth_service_instance = AuthService()
session_repository_instance = SessionRepository()
achievement_repository_instance = AchievementRepository()
session_service_instance = SessionService(session_repository_instance, achievement_repository_instance)

# --- Регистрация Blueprints --- 
# Создаем и регистрируем session_blueprint, передавая ему нужные сервисы
# url_prefix='/' означает, что маршруты из blueprint будут доступны от корня приложения
# (например, /start_session, /finish_session)
session_bp = create_session_blueprint(auth_service_instance, session_service_instance)
app.register_blueprint(session_bp, url_prefix='/')

# --- Глобальные обработчики ошибок (опционально, но рекомендуется) ---
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized", "message": str(error)}), 401

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@app.errorhandler(422)
def unprocessable_entity_error(error):
    # Flask не вызывает этот обработчик для ошибок, возвращенных как tuple, 
    # но его можно использовать для кастомных исключений, если вы их определите.
    return jsonify({"error": "Unprocessable Entity", "message": str(error)}), 422

@app.errorhandler(500)
def internal_server_error(error):
    # Здесь хорошо бы логировать ошибку error
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

# --- Точка входа для локального запуска (не используется Gunicorn/Waitress) ---
if __name__ == '__main__':
    # Переменные окружения FLASK_APP, FLASK_ENV, DEBUG предпочтительнее для `flask run`
    # Этот блок для запуска через `python main.py`
    app.run(host='0.0.0.0', port=8080, debug=True)
