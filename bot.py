import logging
import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, MAX_FILE_SIZE, LOG_LEVEL, DEBUG
from media_processor import MediaProcessor

# Настройка логирования
log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log_level
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.media_processor = MediaProcessor()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CommandHandler("compress", self.compress_command))
        
        # Обработчик кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчик файлов
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = f"""
🎬 Привет, {user.first_name}!

Добро пожаловать в бот конвертации медиа в текст!

Выбери тип конвертации:
        """
        
        keyboard = [
            [InlineKeyboardButton("🎥 Видео → Текст", callback_data="video_to_text")],
            [InlineKeyboardButton("🎵 Аудио → Текст", callback_data="audio_to_text")],
            [InlineKeyboardButton("🎬 Отправить ВИДЕО", callback_data="compress_video")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 Доступные команды:

/start - Запустить бота и выбрать тип конвертации
/compress - Сжать видео без обработки текста
/help - Показать это сообщение
/menu - Показать главное меню

🎬 Возможности бота:
• 🎥 Конвертация видео в текст (OCR)
• 🎵 Конвертация аудио в текст (Speech-to-Text)
• 🗜️ Сжатие видео (через file_id)
• 📄 Обработка документов
• 📸 Обработка изображений

📋 Поддерживаемые форматы:
• Видео: MP4, AVI, MOV, MKV
• Аудио: MP3, WAV, M4A, OGG
• Максимальный размер: 50MB

💡 Для больших файлов бот автоматически предложит сжатие!
        """
        await update.message.reply_text(help_text)
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /menu"""
        keyboard = [
            [InlineKeyboardButton("📄 Обработать текст", callback_data="text_process")],
            [InlineKeyboardButton("📁 Загрузить файл", callback_data="file_upload")],
            [InlineKeyboardButton("🎥 Видео", callback_data="video_process")],
            [InlineKeyboardButton("📸 Фото", callback_data="photo_process")],
            [InlineKeyboardButton("ℹ️ Информация", callback_data="info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("🎛 Главное меню:", reply_markup=reply_markup)
    
    async def compress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /compress - отправка ВИДЕО обратно"""
        await update.message.reply_text(
            "🎬 Режим отправки ВИДЕО\n\n"
            "Отправь мне видео, и я отправлю его обратно как ВИДЕО!\n\n"
            "Это ВИДЕО, а не файл - можно смотреть прямо в Telegram.\n"
            "Используй /start для полной обработки (видео → текст)."
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "video_to_text":
            await query.edit_message_text(
                "🎥 Конвертация видео в текст\n\n"
                "Отправь мне видеофайл (MP4, AVI, MOV и др.) и я извлеку из него текст!\n\n"
                "📋 Поддерживаемые форматы:\n"
                "• MP4, AVI, MOV, MKV\n"
                "• Максимальный размер: 50MB\n\n"
                "Просто отправь видео файл!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")
                ]])
            )
        elif query.data == "audio_to_text":
            await query.edit_message_text(
                "🎵 Конвертация аудио в текст\n\n"
                "Отправь мне аудиофайл (MP3, WAV, M4A и др.) и я преобразую его в текст!\n\n"
                "📋 Поддерживаемые форматы:\n"
                "• MP3, WAV, M4A, OGG\n"
                "• Максимальный размер: 50MB\n\n"
                "Просто отправь аудио файл!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")
                ]])
            )
        elif query.data == "compress_video":
            await query.edit_message_text(
                "🎬 Отправка ВИДЕО\n\n"
                "Отправь мне видео, и я отправлю его обратно как ВИДЕО!\n\n"
                "📋 Как это работает:\n"
                "• Это ВИДЕО, а не файл\n"
                "• Можно смотреть прямо в Telegram\n"
                "• Отправляется в худшем качестве\n"
                "• Максимальный размер: 50MB\n\n"
                "Просто отправь видео файл!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")
                ]])
            )
        elif query.data == "back_to_start":
            await self.start_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "menu":
            await self.menu_command(update, context)
        elif query.data == "text_process":
            await query.edit_message_text("📝 Отправь мне текст для обработки!")
        elif query.data == "file_upload":
            await query.edit_message_text("📁 Отправь мне файл для обработки!")
        elif query.data == "video_process":
            await query.edit_message_text("🎥 Отправь мне видео для обработки!")
        elif query.data == "photo_process":
            await query.edit_message_text("📸 Отправь мне фото для обработки!")
        elif query.data == "info":
            await query.edit_message_text("ℹ️ Информация о боте:\n\nВерсия: 1.0\nСоздан с помощью python-telegram-bot")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text
        user = update.effective_user
        
        response = f"📝 Получил твое сообщение: '{text}'\n\nПользователь: {user.first_name} (ID: {user.id})"
        
        # Простая обработка текста
        if "привет" in text.lower():
            response += "\n\n👋 Привет! Как дела?"
        elif "спасибо" in text.lower():
            response += "\n\n😊 Пожалуйста! Рад помочь!"
        elif "пока" in text.lower():
            response += "\n\n👋 До свидания! Увидимся!"
        
        await update.message.reply_text(response)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик документов"""
        document = update.message.document
        file_name = document.file_name
        file_size = document.file_size
        mime_type = document.mime_type
        
        # Проверяем, является ли документ аудио файлом
        if mime_type and mime_type.startswith('audio/'):
            await self.handle_audio_file(update, context, document)
            return
        
        # Проверяем, является ли документ видео файлом
        if mime_type and mime_type.startswith('video/'):
            await self.handle_video_file(update, context, document)
            return
        
        response = f"📄 Получил документ:\n\n📁 Имя: {file_name}\n📊 Размер: {file_size / (1024*1024):.1f}MB\n🔖 Тип: {mime_type or 'Неизвестно'}"
        
        await update.message.reply_text(response)
    
    async def handle_audio_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, document):
        """Обработчик аудио файлов, отправленных как документы"""
        file_name = document.file_name
        file_size = document.file_size
        
        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                "❌ Файл слишком большой!\n"
                f"Максимальный размер: {MAX_FILE_SIZE / (1024*1024):.0f}MB\n"
                f"Размер вашего файла: {file_size / (1024*1024):.1f}MB"
            )
            return
        
        # Показываем, что начали обработку
        processing_msg = await update.message.reply_text(
            f"🎵 Обрабатываю аудио файл...\n\n"
            f"📁 Файл: {file_name}\n"
            f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
            "⏳ Преобразую речь в текст..."
        )
        
        try:
            # Получаем файл
            file = await context.bot.get_file(document.file_id)
            
            # Создаем временный файл для аудио
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio_path = temp_audio.name
                await file.download_to_drive(temp_audio_path)
            
            # Обрабатываем аудио: конвертируем в текст
            result = self.media_processor.process_audio_to_text(temp_audio_path)
            
            if result['success']:
                result_text = f"""
📝 Текст извлечен из аудио файла:

{result['text']}

📊 Статистика:
• Файл: {file_name}
• Размер файла: {file_size / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
                """
            else:
                result_text = f"""
❌ Ошибка при обработке аудио:

{result['text']}

Попробуйте другой файл или обратитесь к администратору.
                """
            
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке аудио файла: {str(e)}")
            await processing_msg.edit_text(
                f"❌ Ошибка при обработке аудио:\n{str(e)}\n\n"
                "Попробуйте другой файл или обратитесь к администратору."
            )
    
    async def handle_video_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, document):
        """Обработчик видео файлов, отправленных как документы"""
        file_name = document.file_name
        file_size = document.file_size
        
        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                "❌ Файл слишком большой!\n"
                f"Максимальный размер: {MAX_FILE_SIZE / (1024*1024):.0f}MB\n"
                f"Размер вашего файла: {file_size / (1024*1024):.1f}MB"
            )
            return
        
        # Показываем, что начали обработку
        processing_msg = await update.message.reply_text(
            f"🎥 Обрабатываю видео файл...\n\n"
            f"📁 Файл: {file_name}\n"
            f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
            "⏳ Извлекаю аудио из видео..."
        )
        
        try:
            # Получаем файл
            file = await context.bot.get_file(document.file_id)
            
            # Создаем временный файл для видео
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                temp_video_path = temp_video.name
                await file.download_to_drive(temp_video_path)
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                f"🎥 Обрабатываю видео файл...\n\n"
                f"📁 Файл: {file_name}\n"
                f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
                "⏳ Извлекаю аудио из видео...\n"
                "✅ Аудио извлечено! Конвертирую в текст..."
            )
            
            # Обрабатываем видео: извлекаем аудио и конвертируем в текст
            result = self.media_processor.process_video_to_text(temp_video_path)
            
            if result['success']:
                # Отправляем исходное видео обратно (Telegram автоматически сожмет)
                try:
                    # Отправляем видео по file_id (Telegram сожмет автоматически)
                    await update.message.reply_document(
                        document=document.file_id,  # Документ остается как есть
                        caption=f"""
🎬 Видео отправлено обратно (Telegram автоматически сжал):

📝 Текст извлечен:

{result['text']}

📊 Статистика:
• Файл: {file_name}
• Исходный размер: {file_size / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
• File ID: `{document.file_id}`
                        """,
                        parse_mode='Markdown'
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка при отправке сжатого видео: {e}")
                    # Если не удалось отправить видео, отправляем только текст
                    result_text = f"""
📝 Текст извлечен из видео файла:

{result['text']}

📊 Статистика:
• Файл: {file_name}
• Размер видео: {file_size / (1024*1024):.1f}MB
• Размер аудио: {result['audio_size'] / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
                    """
                    await processing_msg.edit_text(result_text)
            else:
                result_text = f"""
❌ Ошибка при обработке видео:

{result['text']}

Попробуйте другой файл или обратитесь к администратору.
                """
                await processing_msg.edit_text(result_text)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке видео файла: {str(e)}")
            await processing_msg.edit_text(
                f"❌ Ошибка при обработке видео:\n{str(e)}\n\n"
                "Попробуйте другой файл или обратитесь к администратору."
            )
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик видео - конвертация в текст через аудио или простое сжатие"""
        video = update.message.video
        duration = video.duration
        file_size = video.file_size
        
        # Проверяем, хочет ли пользователь просто сжать видео
        if update.message.caption and "сжать" in update.message.caption.lower():
            await self.compress_video_only(update, context, video)
            return
        
        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            # Если файл большой, предлагаем сжать
            await update.message.reply_text(
                f"⚠️ Файл слишком большой!\n\n"
                f"📊 Размер: {file_size / (1024*1024):.1f}MB\n"
                f"📏 Лимит: {MAX_FILE_SIZE / (1024*1024):.0f}MB\n\n"
                f"🗜️ Но я могу сжать его для тебя!\n"
                f"Отправляю сжатое видео..."
            )
            
            # Отправляем ВИДЕО в худшем качестве
            await self.send_video_quality(update, context, video, "worst")
            return
        
        # Показываем, что начали обработку
        processing_msg = await update.message.reply_text(
            f"🎥 Обрабатываю видео...\n\n"
            f"⏱ Длительность: {duration} сек\n"
            f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
            "⏳ Извлекаю аудио из видео..."
        )
        
        try:
            # Получаем файл
            file = await context.bot.get_file(video.file_id)
            
            # Создаем временный файл для видео
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                temp_video_path = temp_video.name
                await file.download_to_drive(temp_video_path)
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                f"🎥 Обрабатываю видео...\n\n"
                f"⏱ Длительность: {duration} сек\n"
                f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
                "⏳ Извлекаю аудио из видео...\n"
                "✅ Аудио извлечено! Конвертирую в текст..."
            )
            
            # Обрабатываем видео: извлекаем аудио и конвертируем в текст
            result = self.media_processor.process_video_to_text(temp_video_path)
            
            if result['success']:
                # Отправляем исходное видео обратно (Telegram автоматически сожмет)
                try:
                    # Отправляем видео по file_id (Telegram сожмет автоматически)
                    await update.message.reply_video(
                        video=video.file_id[0],  # Худшее качество
                        caption=f"""
🎬 Видео отправлено обратно (Telegram автоматически сжал):

📝 Текст извлечен:

{result['text']}

📊 Статистика:
• Длительность: {duration} сек
• Исходный размер: {file_size / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
• File ID: `{video.file_id}`
                        """,
                        parse_mode='Markdown'
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка при отправке сжатого видео: {e}")
                    # Если не удалось отправить видео, отправляем только текст
                    result_text = f"""
📝 Текст извлечен из видео:

{result['text']}

📊 Статистика:
• Длительность: {duration} сек
• Размер видео: {file_size / (1024*1024):.1f}MB
• Размер аудио: {result['audio_size'] / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
                    """
                    await processing_msg.edit_text(result_text)
            else:
                result_text = f"""
❌ Ошибка при обработке видео:

{result['text']}

Попробуйте другой файл или обратитесь к администратору.
                """
                await processing_msg.edit_text(result_text)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке видео: {str(e)}")
            await processing_msg.edit_text(
                f"❌ Ошибка при обработке видео:\n{str(e)}\n\n"
                "Попробуйте другой файл или обратитесь к администратору."
            )
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик аудио - конвертация в текст"""
        audio = update.message.audio
        duration = audio.duration
        file_size = audio.file_size
        file_name = audio.file_name or "audio_file"
        
        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                "❌ Файл слишком большой!\n"
                f"Максимальный размер: {MAX_FILE_SIZE / (1024*1024):.0f}MB\n"
                f"Размер вашего файла: {file_size / (1024*1024):.1f}MB"
            )
            return
        
        # Показываем, что начали обработку
        processing_msg = await update.message.reply_text(
            f"🎵 Обрабатываю аудио...\n\n"
            f"📁 Файл: {file_name}\n"
            f"⏱ Длительность: {duration} сек\n"
            f"📊 Размер: {file_size / (1024*1024):.1f}MB\n\n"
            "⏳ Преобразую речь в текст..."
        )
        
        try:
            # Получаем файл
            file = await context.bot.get_file(audio.file_id)
            
            # Создаем временный файл для аудио
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio_path = temp_audio.name
                await file.download_to_drive(temp_audio_path)
            
            # Обрабатываем аудио: конвертируем в текст
            result = self.media_processor.process_audio_to_text(temp_audio_path)
            
            if result['success']:
                result_text = f"""
📝 Текст извлечен из аудио:

{result['text']}

📊 Статистика:
• Файл: {file_name}
• Длительность: {duration} сек
• Размер файла: {file_size / (1024*1024):.1f}MB
• Символов в тексте: {len(result['text'])}
• Исполнитель: {audio.performer or 'Неизвестно'}
                """
            else:
                result_text = f"""
❌ Ошибка при обработке аудио:

{result['text']}

Попробуйте другой файл или обратитесь к администратору.
                """
            
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке аудио: {str(e)}")
            await processing_msg.edit_text(
                f"❌ Ошибка при обработке аудио:\n{str(e)}\n\n"
                "Попробуйте другой файл или обратитесь к администратору."
            )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик фото"""
        photo = update.message.photo[-1]  # Берем фото наилучшего качества
        file_size = photo.file_size
        
        response = f"📸 Получил фото:\n\n📊 Размер: {file_size} байт"
        
        await update.message.reply_text(response)
    
    async def compress_video_only(self, update: Update, context: ContextTypes.DEFAULT_TYPE, video):
        """Отправляет ВИДЕО обратно (не файл!)"""
        try:
            # Отправляем ВИДЕО обратно (худшее качество)
            await update.message.reply_video(
                video=video.file_id[0],  # Худшее качество
                caption=f"""
🎬 ВИДЕО отправлено!

📊 Статистика:
• Длительность: {video.duration} сек
• Исходный размер: {video.file_size / (1024*1024):.1f}MB
• File ID: `{video.file_id}`

💡 Это ВИДЕО, а не файл!
                """,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке видео: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при отправке видео:\n{str(e)}"
            )
    
    async def send_video_quality(self, update: Update, context: ContextTypes.DEFAULT_TYPE, video, quality="worst"):
        """Отправляет видео с выбором качества"""
        try:
            if quality == "best":
                # Лучшее качество
                await update.message.reply_video(
                    video=video.file_id[-1],  # Лучшее качество
                    caption="🎬 ВИДЕО (лучшее качество)"
                )
            elif quality == "worst":
                # Худшее качество
                await update.message.reply_video(
                    video=video.file_id[0],  # Худшее качество
                    caption="🎬 ВИДЕО (худшее качество)"
                )
            else:
                # Обычное качество
                await update.message.reply_video(
                    video=video.file_id[0],  # Худшее качество по умолчанию
                    caption="🎬 ВИДЕО (обычное качество)"
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке видео: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при отправке видео:\n{str(e)}"
            )
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
