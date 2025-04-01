#!/bin/bash
set -e

# Создание виртуального окружения с помощью uv
uv venv

# Активация виртуального окружения
source .venv/bin/activate

# Установка зависимостей с помощью uv
uv pip install -e .
uv pip install -e ".[dev]"

echo "Виртуальное окружение настроено и зависимости установлены!"
echo "Чтобы активировать окружение, используйте команду: source .venv/bin/activate"
