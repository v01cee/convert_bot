#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота
"""

import os
import sys

def check_env_file():
    """Проверяем наличие файла .env"""
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("📋 Создайте файл .env на основе env_example.txt:")
        print("   copy env_example.txt .env")
        print("   Затем отредактируйте .env и добавьте токен бота")
        return False
    return True

def check_dependencies():
    """Проверяем установленные зависимости"""
    try:
        import telegram
        import moviepy
        import pydub
        import speech_recognition
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Не установлена зависимость: {e}")
        print("📦 Установите зависимости: pip install -r requirements.txt")
        return False

def main():
    """Основная функция"""
    print("🤖 Запуск Telegram бота...")
    
    # Проверяем файл .env
    if not check_env_file():
        sys.exit(1)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Запускаем бота
    try:
        from bot import TelegramBot
        bot = TelegramBot()
        print("🚀 Бот запущен! Нажмите Ctrl+C для остановки")
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
