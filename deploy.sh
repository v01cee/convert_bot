#!/bin/bash

# Скрипт для развертывания Telegram бота через Docker

echo "🐳 Развертывание Telegram бота..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с токеном бота:"
    echo "BOT_TOKEN=your_bot_token_here"
    exit 1
fi

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down

# Собираем образ
echo "🔨 Собираем Docker образ..."
docker-compose build

# Запускаем контейнер
echo "🚀 Запускаем бота..."
docker-compose up -d

# Проверяем статус
echo "📊 Проверяем статус..."
docker-compose ps

echo "✅ Бот развернут!"
echo "📋 Полезные команды:"
echo "  docker-compose logs -f          # Просмотр логов"
echo "  docker-compose restart          # Перезапуск"
echo "  docker-compose down             # Остановка"
echo "  docker-compose up -d            # Запуск"
