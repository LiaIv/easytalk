import sys
import os
from pathlib import Path

# Корневая директория проекта (functions)
root_dir = Path(__file__).parent

# Добавляем директорию functions в sys.path и делаем ее основным пакетом
sys.path.insert(0, str(root_dir))

# Инициализируем все модули как части пакета functions
def init_package():
    # Создаем "виртуальные" пакеты для всех модулей
    for directory in ['domain', 'repositories', 'routers', 'services', 'shared']:
        package_name = f'functions.{directory}'
        module = type(sys)(package_name)
        module.__path__ = [str(root_dir / directory)]
        sys.modules[package_name] = module

    # Устанавливаем текущую директорию как директорию functions
    os.chdir(str(root_dir))

init_package()