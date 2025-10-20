# 🚀 Развертывание бота

## Локальный запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/ТВОЙ_USERNAME/telegram-video-audio-to-text-bot.git
cd telegram-video-audio-to-text-bot
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
```bash
# Скопируйте пример файла
copy env_example.txt .env

# Отредактируйте .env и добавьте токен бота
# BOT_TOKEN=ваш_токен_от_BotFather
```

### 4. Запуск бота
```bash
python bot.py
```

## Развертывание на сервере

### Heroku

1. **Создайте Procfile:**
   ```
   worker: python bot.py
   ```

2. **Добавьте переменные окружения в Heroku:**
   ```bash
   heroku config:set BOT_TOKEN=ваш_токен_от_BotFather
   ```

3. **Деплой:**
   ```bash
   git push heroku main
   ```

### VPS/Сервер

1. **Установите Python 3.10+**
2. **Клонируйте репозиторий**
3. **Установите зависимости**
4. **Настройте .env файл**
5. **Запустите через systemd или screen:**
   ```bash
   # Через screen
   screen -S bot
   python bot.py
   # Ctrl+A, D для выхода
   
   # Через systemd (создайте service файл)
   sudo systemctl start telegram-bot
   sudo systemctl enable telegram-bot
   ```

### Docker

1. **Создайте Dockerfile:**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD ["python", "bot.py"]
   ```

2. **Создайте docker-compose.yml:**
   ```yaml
   version: '3.8'
   services:
     bot:
       build: .
       environment:
         - BOT_TOKEN=${BOT_TOKEN}
       restart: unless-stopped
   ```

3. **Запуск:**
   ```bash
   docker-compose up -d
   ```

## Мониторинг

### Логи
```bash
# Просмотр логов
tail -f bot.log

# Через systemd
journalctl -u telegram-bot -f
```

### Перезапуск
```bash
# Через systemd
sudo systemctl restart telegram-bot

# Через Docker
docker-compose restart
```

## Безопасность

- ✅ Токен бота хранится в переменных окружения
- ✅ .env файл не загружается на GitHub
- ✅ Все зависимости зафиксированы в requirements.txt
- ✅ Логирование настроено

## Поддержка

Если возникли проблемы:
1. Проверьте логи
2. Убедитесь, что токен бота правильный
3. Проверьте, что все зависимости установлены
4. Создайте issue в GitHub репозитории
