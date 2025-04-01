#!/bin/bash
set -e

# Активация виртуального окружения, если оно ещё не активировано
if [[ -z "${VIRTUAL_ENV}" ]]; then
    source .venv/bin/activate
fi

# Запуск приложения через uv
export APP_ENV=${APP_ENV:-dev}
echo "Запуск в режиме: $APP_ENV"

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
