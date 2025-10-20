# 🐳 Развертывание через Docker

## Быстрый старт

### 1. **Подготовка:**
```bash
# Клонируем репозиторий
git clone https://github.com/v01cee/convert_bot.git
cd convert_bot

# Создаем .env файл
cp env_example.txt .env
nano .env
# Добавьте: BOT_TOKEN=ваш_токен_от_BotFather
```

### 2. **Запуск через Docker Compose:**
```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем развертывание
./deploy.sh
```

### 3. **Или вручную:**
```bash
# Собираем образ
docker-compose build

# Запускаем бота
docker-compose up -d

# Проверяем статус
docker-compose ps
```

## Управление ботом

### **Основные команды:**
```bash
# Просмотр логов
docker-compose logs -f

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Запуск
docker-compose up -d

# Обновление
docker-compose pull
docker-compose up -d
```

### **Проверка статуса:**
```bash
# Статус контейнеров
docker-compose ps

# Логи бота
docker-compose logs telegram-bot

# Вход в контейнер
docker-compose exec telegram-bot bash
```

## Настройка

### **Переменные окружения:**
```bash
# В .env файле
BOT_TOKEN=ваш_токен_от_BotFather
DEBUG=False
LOG_LEVEL=INFO
```

### **Volumes (если нужны):**
```yaml
# В docker-compose.yml
volumes:
  - ./logs:/app/logs
  - ./temp:/app/temp
```

## Обновление

### **Обновление кода:**
```bash
# Получаем обновления
git pull

# Пересобираем образ
docker-compose build

# Перезапускаем
docker-compose up -d
```

### **Очистка:**
```bash
# Удаление старых образов
docker system prune -a

# Удаление volumes
docker volume prune
```

## Мониторинг

### **Логи:**
```bash
# Все логи
docker-compose logs

# Последние 100 строк
docker-compose logs --tail=100

# Следить за логами
docker-compose logs -f
```

### **Ресурсы:**
```bash
# Использование ресурсов
docker stats

# Информация о контейнере
docker inspect telegram-bot
```

## Безопасность

### **Пользователь:**
- Бот запускается под пользователем `bot` (не root)
- Ограниченные права доступа

### **Сеть:**
- Изолированная Docker сеть
- Нет внешних портов

### **Файлы:**
- Временные файлы удаляются автоматически
- Логи сохраняются в volume

## Troubleshooting

### **Проблемы с запуском:**
```bash
# Проверяем логи
docker-compose logs

# Проверяем конфигурацию
docker-compose config

# Пересобираем образ
docker-compose build --no-cache
```

### **Проблемы с зависимостями:**
```bash
# Обновляем зависимости
docker-compose build --no-cache

# Проверяем образ
docker run --rm telegram-bot python --version
```

## Production

### **Для продакшена:**
```bash
# Используйте Docker Swarm или Kubernetes
# Настройте мониторинг (Prometheus, Grafana)
# Настройте логирование (ELK Stack)
# Настройте backup
```

Готово! 🎉
