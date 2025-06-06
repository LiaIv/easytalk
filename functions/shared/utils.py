# functions/shared/utils.py

import datetime
import pytz
from typing import Any, Dict, List, Optional

def to_iso_datetime(dt: datetime.datetime) -> str:
    """
    Преобразует datetime объект в строку в формате ISO 8601.
    
    Args:
        dt: Объект datetime для преобразования
        
    Returns:
        str: Строка в формате ISO 8601
    """
    if dt.tzinfo is None:
        # Если timezone не указана, используем UTC
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.isoformat()


def from_iso_datetime(iso_str: str) -> datetime.datetime:
    """
    Преобразует строку в формате ISO 8601 в объект datetime.
    
    Args:
        iso_str: Строка даты/времени в формате ISO 8601
        
    Returns:
        datetime.datetime: Объект datetime с timezone
    """
    dt = datetime.datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        # Если timezone не указана, используем UTC
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def firestore_to_dict(doc_snapshot) -> Dict[str, Any]:
    """
    Преобразует Firestore DocumentSnapshot в словарь Python,
    добавляя id документа.
    
    Args:
        doc_snapshot: Firestore DocumentSnapshot
        
    Returns:
        Dict[str, Any]: Данные документа в виде словаря + id
    """
    if not doc_snapshot.exists:
        return {}
        
    result = doc_snapshot.to_dict()
    result['id'] = doc_snapshot.id
    return result


def firestore_to_list(collection_snapshot) -> List[Dict[str, Any]]:
    """
    Преобразует коллекцию Firestore в список словарей Python.
    
    Args:
        collection_snapshot: Результат запроса к Firestore
        
    Returns:
        List[Dict[str, Any]]: Список документов в виде словарей
    """
    return [firestore_to_dict(doc) for doc in collection_snapshot]


def calculate_success_rate(correct: int, total: int) -> float:
    """
    Рассчитывает процент успеха.
    
    Args:
        correct: Число правильных ответов
        total: Общее число ответов
        
    Returns:
        float: Процент успеха от 0.0 до 1.0
    """
    if total == 0:
        return 0.0
    return correct / total
