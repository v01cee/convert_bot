import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Проверяем наличие токена
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменных окружения!\n"
        "Создайте файл .env и добавьте в него:\n"
        "BOT_TOKEN=your_bot_token_here"
    )

# Настройки обработки файлов
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.ogg']

# Настройки очистки файлов
AUTO_DELETE_TEMP_FILES = True  # Автоматически удалять временные файлы
CLEANUP_INTERVAL = 300  # Очистка каждые 5 минут (в секундах)

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
