# functions/services/progress_service.py

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from repositories.progress_repository import ProgressRepository
from domain.progress import ProgressRecord


class ProgressService:
    def __init__(self, progress_repo: ProgressRepository = None):
        self._progress_repo = progress_repo if progress_repo else ProgressRepository()
    
    def record_progress(
        self, 
        user_id: str, 
        score: int, 
        correct_answers: int,
        total_answers: int,
        time_spent: float,
        record_date: Optional[date] = None
    ) -> str:
        """
        Создает запись о прогрессе пользователя.
        
        Args:
            user_id (str): ID пользователя
            score (int): Количество набранных очков
            correct_answers (int): Количество правильных ответов
            total_answers (int): Общее количество ответов
            time_spent (float): Затраченное время в секундах
            record_date (Optional[date]): Дата для записи, если None - используется текущая
            
        Returns:
            str: Идентификатор записи прогресса в формате "{user_id}_{YYYY-MM-DD}"
        """
        # Если дата не указана, используем сегодняшнюю
        if record_date is None:
            record_date = date.today()
            
        # Создаем запись прогресса
        progress_record = ProgressRecord(
            user_id=user_id,
            date=record_date,
            score=score,
            correct_answers=correct_answers,
            total_answers=total_answers,
            time_spent=time_spent
        )
        
        # Сохраняем в репозиторий
        self._progress_repo.record_daily_score(progress_record)
        
        # Возвращаем ID записи
        return f"{user_id}_{record_date.isoformat()}"
    
    def get_progress(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Получает данные о прогрессе пользователя за указанное количество дней.
        
        Args:
            user_id (str): ID пользователя
            days (int): Количество дней для выборки (включая текущий)
            
        Returns:
            Dict с данными прогресса:
            {
                "data": List[Dict] - список записей,
                "total_score": int - общая сумма очков,
                "average_score": float - среднее количество очков в день,
                "success_rate": float - общий процент правильных ответов
            }
        """
        # Рассчитываем даты периода
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)  # -1 т.к. включаем текущий день
        
        # Получаем записи из Firestore
        records = self._get_records_for_period(user_id, start_date, end_date)
        
        # Собираем статистику
        total_score = 0
        total_correct = 0
        total_answers = 0
        data = []
        
        for record in records:
            # Добавляем запись в список данных
            data.append({
                "date": record.date.isoformat(),
                "score": record.score,
                "success_rate": record.success_rate,
                "correct_answers": record.correct_answers,
                "total_answers": record.total_answers,
                "time_spent": record.time_spent
            })
            # Обновляем общую статистику
            total_score += record.score
            total_correct += record.correct_answers
            total_answers += record.total_answers
        
        # Вычисляем средние значения
        record_count = len(records)
        average_score = total_score / record_count if record_count > 0 else 0
        success_rate = total_correct / total_answers if total_answers > 0 else 0
        
        return {
            "data": data,
            "total_score": total_score,
            "average_score": round(average_score, 1),
            "success_rate": round(success_rate, 2)
        }
    
    def get_weekly_summary(self, user_id: str) -> int:
        """
        Получает общую сумму очков за последнюю неделю.
        
        Args:
            user_id (str): ID пользователя
            
        Returns:
            int: Сумма очков за последнюю неделю
        """
        week_ago = datetime.now() - timedelta(days=7)
        return self._progress_repo.sum_scores_for_week(user_id, week_ago)
    
    def _get_records_for_period(self, user_id: str, start_date: date, end_date: date) -> List[ProgressRecord]:
        """
        Внутренний метод для получения записей прогресса за указанный период.
        
        Args:
            user_id (str): ID пользователя
            start_date (date): Начальная дата периода
            end_date (date): Конечная дата периода
            
        Returns:
            List[ProgressRecord]: Список записей прогресса
        """
        # Преобразуем даты в строковый формат для запроса к репозиторию
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        # Вызываем метод get_progress из репозитория
        return self._progress_repo.get_progress(user_id, start_date_str, end_date_str)
