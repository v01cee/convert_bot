"""
Модуль для очистки временных файлов
"""

import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def cleanup_temp_files(temp_dir: str = None, max_age_hours: int = 1):
    """
    Очищает временные файлы старше указанного возраста
    
    Args:
        temp_dir: Директория с временными файлами (по умолчанию системная)
        max_age_hours: Максимальный возраст файлов в часах
    """
    if not temp_dir:
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    
    # Создаем директорию, если её нет
    os.makedirs(temp_dir, exist_ok=True)
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    cleaned_count = 0
    total_size = 0
    
    try:
        for file_path in Path(temp_dir).glob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"🗑️ Удален старый файл: {file_path.name} ({file_size / 1024:.1f}KB)")
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось удалить файл {file_path.name}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"✅ Очистка завершена: удалено {cleaned_count} файлов, освобождено {total_size / 1024:.1f}KB")
        else:
            logger.debug("🧹 Старых файлов для очистки не найдено")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке временных файлов: {e}")

def cleanup_old_files():
    """Очищает файлы старше 1 часа"""
    cleanup_temp_files(max_age_hours=1)

def cleanup_very_old_files():
    """Очищает файлы старше 24 часов"""
    cleanup_temp_files(max_age_hours=24)

if __name__ == "__main__":
    # Тестовая очистка
    cleanup_temp_files()
