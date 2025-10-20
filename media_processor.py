import os
import tempfile
import logging
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
from moviepy.video.fx import resize

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def compress_video_for_processing(self, video_path: str, max_size_mb: int = 45) -> str:
        """
        Сжимает видео до размера меньше max_size_mb, сохраняя качество аудио
        
        Args:
            video_path: Путь к исходному видео
            max_size_mb: Максимальный размер в MB
            
        Returns:
            str: Путь к сжатому видео
        """
        try:
            logger.info(f"Сжимаю видео: {video_path}")
            
            # Создаем временный файл для сжатого видео
            temp_dir = tempfile.gettempdir()
            compressed_path = os.path.join(temp_dir, f"compressed_{os.getpid()}.mp4")
            
            # Загружаем видео
            video = VideoFileClip(video_path)
            
            # Получаем текущий размер
            current_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"Исходный размер: {current_size_mb:.1f}MB")
            
            # Если файл уже меньше лимита, возвращаем исходный
            if current_size_mb <= max_size_mb:
                logger.info("Файл уже подходящего размера")
                video.close()
                return video_path
            
            # Настраиваем сжатие
            # Видео: низкое качество, аудио: высокое качество
            compressed_video = video.resize(height=360)  # 360p для видео
            
            # Сохраняем с высоким качеством аудио
            compressed_video.write_videofile(
                compressed_path,
                audio_codec='aac',
                audio_bitrate='128k',  # Высокое качество аудио
                video_codec='libx264',
                preset='fast',  # Быстрое сжатие
                ffmpeg_params=['-crf', '28'],  # Низкое качество видео
                verbose=False,
                logger=None
            )
            
            # Закрываем файлы
            compressed_video.close()
            video.close()
            
            # Проверяем размер сжатого файла
            compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
            logger.info(f"Сжатый размер: {compressed_size_mb:.1f}MB")
            
            # Если все еще большой, сжимаем еще больше
            if compressed_size_mb > max_size_mb:
                logger.info("Дополнительное сжатие...")
                video = VideoFileClip(compressed_path)
                ultra_compressed = video.resize(height=240)  # 240p
                
                ultra_compressed.write_videofile(
                    compressed_path,
                    audio_codec='aac',
                    audio_bitrate='128k',
                    video_codec='libx264',
                    preset='fast',
                    ffmpeg_params=['-crf', '32'],  # Еще ниже качество видео
                    verbose=False,
                    logger=None
                )
                
                ultra_compressed.close()
                video.close()
                
                final_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
                logger.info(f"Финальный размер: {final_size_mb:.1f}MB")
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"Ошибка при сжатии видео: {str(e)}")
            # В случае ошибки возвращаем исходный файл
            return video_path
    
    def compress_video_for_user(self, video_path: str, target_size_mb: int = 5) -> str:
        """
        Сжимает видео для отправки пользователю (минимальный размер, хороший звук)
        
        Args:
            video_path: Путь к исходному видео
            target_size_mb: Целевой размер в MB
            
        Returns:
            str: Путь к сжатому видео
        """
        try:
            logger.info(f"Сжимаю видео для пользователя: {video_path}")
            
            # Создаем временный файл для сжатого видео
            temp_dir = tempfile.gettempdir()
            compressed_path = os.path.join(temp_dir, f"user_compressed_{os.getpid()}.mp4")
            
            # Загружаем видео
            video = VideoFileClip(video_path)
            
            # Агрессивное сжатие для минимального размера
            # Видео: очень низкое качество, аудио: хорошее качество
            compressed_video = video.resize(height=240)  # 240p
            
            # Сохраняем с оптимальными настройками
            compressed_video.write_videofile(
                compressed_path,
                audio_codec='aac',
                audio_bitrate='96k',  # Хорошее качество аудио
                video_codec='libx264',
                preset='ultrafast',  # Максимальная скорость
                ffmpeg_params=[
                    '-crf', '35',  # Очень низкое качество видео
                    '-movflags', '+faststart'  # Быстрая загрузка
                ],
                verbose=False,
                logger=None
            )
            
            # Закрываем файлы
            compressed_video.close()
            video.close()
            
            # Проверяем размер
            final_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
            logger.info(f"Сжатое видео: {final_size_mb:.1f}MB")
            
            # Если все еще большой, сжимаем еще больше
            if final_size_mb > target_size_mb:
                logger.info("Дополнительное сжатие до минимума...")
                video = VideoFileClip(compressed_path)
                ultra_compressed = video.resize(height=180)  # 180p
                
                ultra_compressed.write_videofile(
                    compressed_path,
                    audio_codec='aac',
                    audio_bitrate='64k',  # Минимальное качество аудио
                    video_codec='libx264',
                    preset='ultrafast',
                    ffmpeg_params=[
                        '-crf', '40',  # Минимальное качество видео
                        '-movflags', '+faststart'
                    ],
                    verbose=False,
                    logger=None
                )
                
                ultra_compressed.close()
                video.close()
                
                final_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
                logger.info(f"Ультра-сжатое видео: {final_size_mb:.1f}MB")
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"Ошибка при сжатии видео для пользователя: {str(e)}")
            # В случае ошибки возвращаем исходный файл
            return video_path
    
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
        Полный процесс: видео -> сжатие -> аудио -> текст
        
        Args:
            video_path: Путь к видео файлу
            language: Язык для распознавания
            
        Returns:
            dict: Результат обработки с текстом и метаданными
        """
        temp_audio_path = None
        compressed_video_path = None
        try:
            # Шаг 0: Сжимаем видео если нужно
            original_size = os.path.getsize(video_path)
            original_size_mb = original_size / (1024 * 1024)
            
            if original_size_mb > 45:  # Если больше 45MB, сжимаем
                logger.info(f"Сжимаю большое видео: {original_size_mb:.1f}MB")
                compressed_video_path = self.compress_video_for_processing(video_path)
                processing_video_path = compressed_video_path
            else:
                processing_video_path = video_path
            
            # Шаг 1: Извлекаем аудио из видео
            temp_audio_path = self.extract_audio_from_video(processing_video_path)
            
            # Шаг 2: Конвертируем аудио в текст
            text = self.convert_audio_to_text(temp_audio_path, language)
            
            # Получаем информацию о файлах
            final_video_size = os.path.getsize(processing_video_path)
            audio_size = os.path.getsize(temp_audio_path) if temp_audio_path else 0
            
            return {
                'success': True,
                'text': text,
                'original_size': original_size,
                'video_size': final_video_size,
                'audio_size': audio_size,
                'compressed': compressed_video_path is not None,
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
            
            # Удаляем сжатое видео (если было создано)
            if compressed_video_path and os.path.exists(compressed_video_path):
                try:
                    os.remove(compressed_video_path)
                    logger.info(f"✅ Сжатое видео удалено: {compressed_video_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить сжатое видео: {e}")
            
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
