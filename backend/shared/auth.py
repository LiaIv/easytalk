from fastapi import Header, HTTPException, status, Depends
from firebase_admin import auth as firebase_auth_module # Переименовываем, чтобы избежать конфликта с переменной auth

from services.auth_service import AuthService

async def get_current_user_id(
    authorization: str = Header(None),
    auth_service: AuthService = Depends(AuthService) # Внедряем AuthService напрямую
) -> str:
    """
    Извлекает и верифицирует токен Firebase ID из заголовка Authorization.
    Возвращает UID пользователя в случае успеха.
    
    В случае ошибки вызывает HTTPException с соответствующим статус-кодом.
    
    Использование в маршрутах:
    @app.get("/protected-endpoint")
    async def protected_endpoint(uid: str = Depends(get_current_user_id)):
        # uid доступен здесь как строка с идентификатором пользователя
        return {"message": f"Hello, user {uid}"}
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Authorization header is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    try:
        # Используем внедренный auth_service
        uid_or_payload = await auth_service.verify_token(token)
        
        # Современная версия verify_token возвращает строку UID
        if isinstance(uid_or_payload, str):
            return uid_or_payload
        
        # Обратная совместимость: если вернулся словарь, извлекаем uid
        if isinstance(uid_or_payload, dict) and "uid" in uid_or_payload:
            return uid_or_payload["uid"]
        
        # Иначе — ошибка аутентификации
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: UID not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
    except firebase_auth_module.InvalidIdTokenError as e: # Используем переименованный импорт
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Логирование ошибки e
        print(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials due to an unexpected error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
