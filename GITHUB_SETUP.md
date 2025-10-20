# 🚀 Настройка GitHub репозитория

## 1. Создай репозиторий на GitHub

1. Перейди на [GitHub.com](https://github.com)
2. Нажми **"New repository"** (зеленая кнопка)
3. Заполни данные:
   - **Repository name**: `telegram-video-audio-to-text-bot`
   - **Description**: `Telegram bot for converting video and audio files to text using speech recognition`
   - **Visibility**: Public (или Private, если хочешь)
   - **НЕ** добавляй README, .gitignore, license (у нас уже есть)

## 2. Подключи локальный репозиторий к GitHub

Открой терминал в папке проекта и выполни:

```bash
# Инициализация Git (если еще не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Telegram bot for video/audio to text conversion"

# Подключение к GitHub репозиторию (замени URL на свой)
git remote add origin https://github.com/ТВОЙ_USERNAME/telegram-video-audio-to-text-bot.git

# Отправка на GitHub
git branch -M main
git push -u origin main
```

## 3. Структура проекта

```
telegram-video-audio-to-text-bot/
├── bot.py                 # Основной файл бота
├── media_processor.py     # Обработка видео и аудио
├── config.py             # Конфигурация
├── requirements.txt      # Зависимости
├── run_bot.py           # Скрипт запуска
├── env_example.txt      # Пример переменных окружения
├── .gitignore           # Игнорируемые файлы
├── .env                 # Переменные окружения (НЕ загружается)
├── README.md            # Документация
├── QUICK_START.md       # Быстрый старт
├── GITHUB_SETUP.md      # Эта инструкция
└── LICENSE              # Лицензия MIT
```

## 4. Важные файлы

- ✅ **.env** - НЕ загружается на GitHub (в .gitignore)
- ✅ **Токен бота** - хранится только локально в .env
- ✅ **Все зависимости** - указаны в requirements.txt
- ✅ **Документация** - полная в README.md

## 5. После загрузки

Другие пользователи смогут:

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Создать .env файл с токеном бота
4. Запустить бота: `python bot.py`

## 6. Обновление репозитория

```bash
# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить на GitHub
git push
```

Готово! 🎉
