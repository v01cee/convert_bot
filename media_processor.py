import os
import tempfile
import logging
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def extract_audio_from_video(self, video_path: str, output_audio_path: str = None) -> str:
        """
        Извлекает аудио из видео файла и сохраняет как MP3
        
        Args:
            video_path: Путь к видео файлу
            output_audio_path: Путь для сохранения аудио (опционально)
            
        Returns:
            str: Путь к извлеченному аудио файлу
        """
        try:
            # Создаем временный файл для аудио, если путь не указан
            if not output_audio_path:
                temp_dir = tempfile.gettempdir()
                output_audio_path = os.path.join(temp_dir, f"extracted_audio_{os.getpid()}.mp3")
            
            logger.info(f"Извлекаю аудио из видео: {video_path}")
            
            # Загружаем видео
            video = VideoFileClip(video_path)
            
            # Извлекаем аудио
            audio = video.audio
            
            if audio is None:
                raise ValueError("В видео файле нет аудио дорожки")
            
            # Сохраняем как MP3
            audio.write_audiofile(output_audio_path, verbose=False, logger=None)
            
            # Закрываем файлы
            audio.close()
            video.close()
            
            logger.info(f"Аудио успешно извлечено: {output_audio_path}")
            return output_audio_path
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении аудио: {str(e)}")
            raise
    
    def convert_audio_to_text(self, audio_path: str, language: str = 'ru') -> str:
        """
        Конвертирует аудио файл в текст
        
        Args:
            audio_path: Путь к аудио файлу
            language: Язык для распознавания (по умолчанию русский)
            
        Returns:
            str: Распознанный текст
        """
        try:
            logger.info(f"Конвертирую аудио в текст: {audio_path}")
            
            # Загружаем аудио файл
            audio = AudioSegment.from_file(audio_path)
            
            # Конвертируем в формат, подходящий для speech_recognition
            wav_data = audio.export(format="wav").read()
            
            # Распознаем речь
            with sr.AudioData(wav_data, audio.frame_rate, audio.sample_width) as source:
                # Убираем шум
                self.recognizer.adjust_for_ambient_noise(source)
                # Распознаем речь
                text = self.recognizer.recognize_google(source, language=language)
            
            logger.info(f"Текст успешно распознан, длина: {len(text)} символов")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Не удалось распознать речь в аудио файле")
            return "❌ Не удалось распознать речь в аудио файле. Возможно, файл слишком тихий или содержит только музыку."
            
        except sr.RequestError as e:
            logger.error(f"Ошибка сервиса распознавания речи: {str(e)}")
            return f"❌ Ошибка сервиса распознавания речи: {str(e)}"
            
        except Exception as e:
            logger.error(f"Ошибка при конвертации аудио в текст: {str(e)}")
            return f"❌ Ошибка при обработке аудио: {str(e)}"
    
    def process_video_to_text(self, video_path: str, language: str = 'ru') -> dict:
        """
        Полный процесс: видео -> аудио -> текст
        
        Args:
            video_path: Путь к видео файлу
            language: Язык для распознавания
            
        Returns:
            dict: Результат обработки с текстом и метаданными
        """
        temp_audio_path = None
        try:
            # Шаг 1: Извлекаем аудио из видео
            temp_audio_path = self.extract_audio_from_video(video_path)
            
            # Шаг 2: Конвертируем аудио в текст
            text = self.convert_audio_to_text(temp_audio_path, language)
            
            # Получаем информацию о файлах
            video_size = os.path.getsize(video_path)
            audio_size = os.path.getsize(temp_audio_path) if temp_audio_path else 0
            
            return {
                'success': True,
                'text': text,
                'video_size': video_size,
                'audio_size': audio_size,
                'temp_audio_path': temp_audio_path
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке видео: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': f"❌ Ошибка при обработке видео: {str(e)}"
            }
        
        finally:
            # Удаляем временный аудио файл
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    logger.info(f"✅ Временный аудио файл удален: {temp_audio_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить временный файл: {e}")
            
            # Удаляем исходный видео файл
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    logger.info(f"✅ Исходный видео файл удален: {video_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить исходный файл: {e}")
    
    def process_audio_to_text(self, audio_path: str, language: str = 'ru') -> dict:
        """
        Конвертирует аудио файл в текст
        
        Args:
            audio_path: Путь к аудио файлу
            language: Язык для распознавания
            
        Returns:
            dict: Результат обработки с текстом и метаданными
        """
        try:
            # Конвертируем аудио в текст
            text = self.convert_audio_to_text(audio_path, language)
            
            # Получаем информацию о файле
            audio_size = os.path.getsize(audio_path)
            
            return {
                'success': True,
                'text': text,
                'audio_size': audio_size
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке аудио: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': f"❌ Ошибка при обработке аудио: {str(e)}"
            }
        
        finally:
            # Удаляем исходный аудио файл
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    logger.info(f"✅ Исходный аудио файл удален: {audio_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить исходный файл: {e}")
