# functions/routers/session_router.py
from flask import Blueprint, request, jsonify
from domain.session import RoundDetail # Убедитесь, что модель RoundDetail импортируется правильно

def create_session_blueprint(auth_service, session_service):
    session_bp = Blueprint('session_router', __name__)

    @session_bp.route("/start_session", methods=["POST"])
    def start_session_handler():
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        try:
            uid = auth_service.verify_token(token)
        except Exception as e:
            # В реальном приложении здесь стоит логировать ошибку 'e'
            return jsonify({"error": "Unauthorized", "message": str(e)}), 401

        data = request.get_json(silent=True) or {}
        game_type = data.get("gameType")
        if game_type not in ("guess_animal", "build_sentence"):
            return jsonify({"error": "Invalid gameType"}), 422

        try:
            session_id = session_service.start_session(uid, game_type)
            return jsonify({"sessionId": session_id}), 200
        except Exception as e:
            # В реальном приложении здесь стоит логировать ошибку 'e'
            return jsonify({"error": "Failed to start session", "message": str(e)}), 500

    @session_bp.route("/finish_session", methods=["PATCH"])
    def finish_session_handler():
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        try:
            uid = auth_service.verify_token(token)
        except Exception as e:
            # В реальном приложении здесь стоит логировать ошибку 'e'
            return jsonify({"error": "Unauthorized", "message": str(e)}), 401

        session_id = request.args.get("sessionId")
        if not session_id:
            return jsonify({"error": "Missing sessionId"}), 422

        data = request.get_json(silent=True) or {}
        details_raw = data.get("details")
        score = data.get("score")

        if not isinstance(details_raw, list):
            # Можно добавить более конкретную проверку, если требуется (например, на длину списка)
            return jsonify({"error": "Details must be a list"}), 422
        
        parsed_details = []
        try:
            for detail_data in details_raw:
                # Используем RoundDetail(**detail_data) для Pydantic моделей
                # Убедитесь, что RoundDetail может быть инициализирован таким образом
                parsed_details.append(RoundDetail(**detail_data))
        except TypeError as te: # Если **detail_data не подходит для RoundDetail
             return jsonify({"error": f"Invalid format in round details: {str(te)}"}), 422
        except Exception as e: # Другие возможные ошибки при парсинге
            return jsonify({"error": f"Error parsing round details: {str(e)}"}), 422

        if not isinstance(score, int):
            return jsonify({"error": "Score must be an integer"}), 422

        try:
            session_service.finish_session(uid, session_id, parsed_details, score)
            return jsonify({"message": "Session finished successfully"}), 200
        except ValueError as e: # Например, если сессия не найдена в session_service
            return jsonify({"error": str(e)}), 404 
        except Exception as e:
            # В реальном приложении здесь стоит логировать ошибку 'e'
            return jsonify({"error": "Failed to finish session", "message": str(e)}), 500
            
    return session_bp
