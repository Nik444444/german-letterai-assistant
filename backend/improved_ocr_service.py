import os
import logging
import tempfile
import base64
import requests
import json
import io
from typing import Optional, Tuple, List
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
import asyncio
from datetime import datetime
import mimetypes

# Импорт Tesseract OCR
import pytesseract
import cv2
import numpy as np

# Импорт LLM manager для Vision анализа
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class ImprovedOCRService:
    """
    Улучшенный OCR сервис с множественными методами извлечения текста:
    1. Tesseract OCR (основной метод) - традиционный OCR с поддержкой многих языков
    2. LLM Vision (fallback) - Gemini Pro Vision, GPT-4V, Claude 3.5 Sonnet
    3. Бесплатные Online OCR API (fallback)
    4. Базовое извлечение текста из PDF
    """
    
    def __init__(self):
        self.ocr_space_api_key = os.environ.get('OCR_SPACE_API_KEY')
        self.azure_vision_key = os.environ.get('AZURE_COMPUTER_VISION_KEY')
        self.azure_vision_endpoint = os.environ.get('AZURE_COMPUTER_VISION_ENDPOINT')
        
        # Проверяем доступность различных методов
        self.tesseract_available = self._check_tesseract_availability()
        self.llm_vision_available = self._check_llm_vision_availability()
        self.ocr_space_available = bool(self.ocr_space_api_key)
        self.azure_vision_available = bool(self.azure_vision_key and self.azure_vision_endpoint)
        
        # Настройка tesseract конфигурации
        self.tesseract_config = '--oem 3 --psm 6 -l ukr+rus+deu+eng'
        self.tesseract_config_document = '--oem 3 --psm 4 -l ukr+rus+deu+eng'
        self.tesseract_config_single_block = '--oem 3 --psm 6 -l ukr+rus+deu+eng'
        
        logger.info(f"Improved OCR Service initialized:")
        logger.info(f"  - Tesseract OCR available: {self.tesseract_available}")
        logger.info(f"  - LLM Vision available: {self.llm_vision_available}")
        logger.info(f"  - OCR.space available: {self.ocr_space_available}")
        logger.info(f"  - Azure Vision available: {self.azure_vision_available}")
    
    def _check_tesseract_availability(self) -> bool:
        """Проверка доступности Tesseract OCR"""
        try:
            # Проверяем переменную окружения
            tesseract_available = os.environ.get('TESSERACT_AVAILABLE', 'true').lower()
            if tesseract_available == 'false':
                logger.warning("TESSERACT_AVAILABLE=false - OCR functionality disabled")
                return False
            
            # Проверяем, что tesseract установлен
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            
            # Проверяем доступные языки
            languages = pytesseract.get_languages()
            logger.info(f"Available languages: {languages}")
            
            # Проверяем наличие необходимых языков
            required_langs = ['rus', 'deu', 'eng', 'ukr']
            missing_langs = [lang for lang in required_langs if lang not in languages]
            
            if missing_langs:
                logger.warning(f"Missing language packs: {missing_langs}")
                # Используем только доступные языки
                available_langs = [lang for lang in required_langs if lang in languages]
                if available_langs:
                    self.tesseract_config = f'--oem 3 --psm 6 -l {"+".join(available_langs)}'
                    self.tesseract_config_document = f'--oem 3 --psm 4 -l {"+".join(available_langs)}'
                    self.tesseract_config_single_block = f'--oem 3 --psm 6 -l {"+".join(available_langs)}'
                    logger.info(f"Using available languages: {available_langs}")
                else:
                    # Fallback to English only
                    self.tesseract_config = '--oem 3 --psm 6 -l eng'
                    self.tesseract_config_document = '--oem 3 --psm 4 -l eng'
                    self.tesseract_config_single_block = '--oem 3 --psm 6 -l eng'
                    logger.warning("Fallback to English only OCR")
            else:
                logger.info("All required language packs are available")
                
            return True
            
        except Exception as e:
            logger.error(f"Tesseract check failed: {e}")
            return False
    
    def _check_llm_vision_availability(self) -> bool:
        """Проверка доступности LLM Vision через modern_llm_manager"""
        try:
            # Проверяем, есть ли хотя бы один активный системный провайдер
            providers = modern_llm_manager.get_available_providers()
            has_system_providers = any(providers.values())
            
            # Также проверяем, есть ли хотя бы одна модель в статусе провайдеров
            status = modern_llm_manager.get_provider_status()
            has_configured_providers = len(status) > 0
            
            # LLM Vision доступен если есть конфигурированные провайдеры (даже если не активны)
            # потому что пользователи могут передавать свои API ключи
            available = has_system_providers or has_configured_providers
            
            logger.info(f"LLM Vision availability check: system_providers={has_system_providers}, configured_providers={has_configured_providers}, available={available}")
            return available
        except Exception as e:
            logger.warning(f"LLM Vision check failed: {e}")
            return False
    
    def _safe_tesseract_call(self, image, config):
        """Безопасный вызов tesseract с обработкой ошибок"""
        try:
            if not self.tesseract_available:
                logger.warning("Tesseract not available for OCR call")
                return ""
                
            result = pytesseract.image_to_string(image, config=config)
            return result.strip() if result else ""
        except Exception as e:
            logger.warning(f"Tesseract call failed with config '{config}': {e}")
            return ""
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Продвинутое улучшение изображения для супер-качественного OCR"""
        try:
            # Конвертируем в numpy array
            img_array = np.array(image)
            
            # Если изображение цветное, конвертируем в серый
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Продвинутое улучшение качества
            # 1. Адаптивная гауссова фильтрация для удаления шума
            img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
            
            # 2. Улучшение контраста с помощью CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img_array = clahe.apply(img_array)
            
            # 3. Морфологические операции для очистки текста
            kernel = np.ones((2,2), np.uint8)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel)
            
            # 4. Адаптивная пороговая обработка
            img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 5. Дополнительное увеличение размера для лучшего OCR
            height, width = img_array.shape
            if width < 1500:  # Увеличиваем целевой размер
                scale_factor = 1500 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 6. Дополнительное повышение резкости
            kernel_sharpen = np.array([[-1,-1,-1], 
                                     [-1, 9,-1], 
                                     [-1,-1,-1]])
            img_array = cv2.filter2D(img_array, -1, kernel_sharpen)
            
            # Конвертируем обратно в PIL Image
            enhanced_image = Image.fromarray(img_array)
            
            return enhanced_image
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image  # Возвращаем оригинальное изображение в случае ошибки
    
    async def extract_text_with_tesseract(self, image_path: str) -> str:
        """
        Извлечение текста с помощью Tesseract OCR (основной метод)
        """
        try:
            if not self.tesseract_available:
                logger.warning("Tesseract OCR is not available")
                return ""
            
            # Открываем изображение
            image = Image.open(image_path)
            
            # Улучшаем качество изображения для OCR
            enhanced_image = self._enhance_image_for_ocr(image)
            
            # Пробуем разные конфигурации OCR
            text_results = []
            
            # Конфигурация для документов
            try:
                text1 = self._safe_tesseract_call(enhanced_image, self.tesseract_config_document)
                if text1:
                    text_results.append(text1)
            except Exception as e:
                logger.warning(f"Tesseract document config failed: {e}")
            
            # Конфигурация для одного блока
            try:
                text2 = self._safe_tesseract_call(enhanced_image, self.tesseract_config_single_block)
                if text2:
                    text_results.append(text2)
            except Exception as e:
                logger.warning(f"Tesseract single block config failed: {e}")
            
            # Стандартная конфигурация
            try:
                text3 = self._safe_tesseract_call(enhanced_image, self.tesseract_config)
                if text3:
                    text_results.append(text3)
            except Exception as e:
                logger.warning(f"Tesseract standard config failed: {e}")
            
            # Выбираем наиболее длинный результат
            if text_results:
                best_text = max(text_results, key=len)
                logger.info(f"Tesseract OCR extracted {len(best_text)} characters")
                return best_text
            else:
                logger.warning("No text extracted with Tesseract")
                return ""
                
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    async def extract_text_with_llm_vision(self, image_path: str, user_providers: List = None) -> str:
        """
        Извлечение текста с помощью LLM Vision (основной метод)
        Использует Gemini Pro Vision, GPT-4V, Claude 3.5 Sonnet
        """
        try:
            # Создаем специальный промпт для извлечения текста
            ocr_prompt = """
            ВАЖНО: Ваша задача - извлечь ВСЕ текст из изображения с максимальной точностью.

            Инструкции:
            1. Внимательно проанализируйте изображение
            2. Извлеките ВЕСЬ видимый текст, включая:
               - Заголовки и подзаголовки
               - Основной текст
               - Подписи к изображениям
               - Номера страниц
               - Даты и адреса
               - Любые другие текстовые элементы
            3. Сохраните оригинальное форматирование (абзацы, списки)
            4. НЕ интерпретируйте содержание - только извлекайте текст
            5. Если текст на нескольких языках, извлеките все
            6. Если текст плохо видим, укажите это: [неразборчиво]

            Отвечайте ТОЛЬКО извлеченным текстом, без дополнительных комментариев.
            """
            
            # Если есть пользовательские провайдеры, используем их
            if user_providers:
                for provider_type, model_name, api_key in user_providers:
                    try:
                        provider = modern_llm_manager.create_user_provider(provider_type, model_name, api_key)
                        result = await provider.generate_content(ocr_prompt, image_path)
                        if result and len(result.strip()) > 20:  # Проверяем, что получили достаточно текста
                            logger.info(f"LLM Vision ({provider_type}) extracted {len(result)} characters")
                            return result.strip()
                    except Exception as e:
                        logger.warning(f"LLM Vision provider {provider_type} failed: {e}")
                        continue
            
            # Если пользовательские провайдеры не работают, используем системные
            try:
                result, provider_name = await modern_llm_manager.generate_content(ocr_prompt, image_path)
                if result and len(result.strip()) > 20:
                    logger.info(f"LLM Vision ({provider_name}) extracted {len(result)} characters")
                    return result.strip()
            except Exception as e:
                logger.warning(f"System LLM Vision failed: {e}")
            
            return ""
            
        except Exception as e:
            logger.error(f"LLM Vision OCR failed: {e}")
            return ""
    
    async def extract_text_with_ocr_space(self, image_path: str) -> str:
        """
        Извлечение текста с помощью OCR.space API (бесплатный лимит: 25,000 запросов/месяц)
        """
        try:
            if not self.ocr_space_available:
                logger.warning("OCR.space API key not available")
                return ""
            
            url = "https://api.ocr.space/parse/image"
            
            # Читаем изображение
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Подготавливаем данные для запроса
            files = {
                'file': ('image.jpg', image_data, 'image/jpeg')
            }
            
            data = {
                'apikey': self.ocr_space_api_key,
                'language': 'ger,eng,rus',  # Немецкий, английский, русский
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'OCREngine': 2,  # Использовать улучшенный движок
                'isTable': True  # Лучше обрабатывать таблицы
            }
            
            # Отправляем запрос
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Извлекаем текст из ответа
            if result.get('OCRExitCode') == 1 and result.get('ParsedResults'):
                parsed_text = result['ParsedResults'][0].get('ParsedText', '')
                if parsed_text:
                    logger.info(f"OCR.space extracted {len(parsed_text)} characters")
                    return parsed_text.strip()
            
            error_msg = result.get('ErrorMessage', 'Unknown error')
            logger.warning(f"OCR.space API error: {error_msg}")
            return ""
            
        except Exception as e:
            logger.error(f"OCR.space API failed: {e}")
            return ""
    
    async def extract_text_with_azure_vision(self, image_path: str) -> str:
        """
        Извлечение текста с помощью Azure Computer Vision API (бесплатный лимит)
        """
        try:
            if not self.azure_vision_available:
                logger.warning("Azure Computer Vision API not configured")
                return ""
            
            # Читаем изображение
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # URL для Read API
            read_url = f"{self.azure_vision_endpoint}/vision/v3.2/read/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            # Отправляем изображение на анализ
            response = requests.post(read_url, headers=headers, data=image_data, timeout=30)
            response.raise_for_status()
            
            # Получаем ID операции
            operation_location = response.headers.get('Operation-Location')
            if not operation_location:
                logger.error("Azure Vision: No Operation-Location header")
                return ""
            
            # Ждем завершения анализа
            result_url = operation_location
            max_attempts = 10
            
            for attempt in range(max_attempts):
                await asyncio.sleep(1)  # Ждем 1 секунду
                
                result_response = requests.get(result_url, headers={'Ocp-Apim-Subscription-Key': self.azure_vision_key})
                result_response.raise_for_status()
                
                result = result_response.json()
                status = result.get('status')
                
                if status == 'succeeded':
                    # Извлекаем текст
                    text_lines = []
                    if 'analyzeResult' in result:
                        for page in result['analyzeResult'].get('readResults', []):
                            for line in page.get('lines', []):
                                text_lines.append(line.get('text', ''))
                    
                    extracted_text = '\n'.join(text_lines)
                    if extracted_text:
                        logger.info(f"Azure Vision extracted {len(extracted_text)} characters")
                        return extracted_text.strip()
                    
                elif status == 'failed':
                    logger.error("Azure Vision analysis failed")
                    return ""
                elif status == 'running':
                    continue
                else:
                    logger.warning(f"Azure Vision unknown status: {status}")
                    return ""
            
            logger.error("Azure Vision analysis timeout")
            return ""
            
        except Exception as e:
            logger.error(f"Azure Vision API failed: {e}")
            return ""
    
    def extract_text_from_pdf_direct(self, pdf_path: str) -> str:
        """Прямое извлечение текста из PDF (без OCR)"""
        try:
            extracted_text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        extracted_text += text + "\n"
            
            if extracted_text.strip():
                logger.info(f"Direct PDF extraction: {len(extracted_text)} characters")
                return extracted_text.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Direct PDF extraction failed: {e}")
            return ""
    
    async def extract_text_from_image(self, image_path: str, user_providers: List = None) -> str:
        """
        Извлечение текста из изображения с использованием нескольких методов
        Приоритет: Tesseract OCR (основной) -> LLM Vision -> Online OCR APIs
        """
        try:
            logger.info(f"Starting image OCR for: {image_path}")
            
            # Метод 1: Tesseract OCR (основной метод)
            if self.tesseract_available:
                try:
                    text = await self.extract_text_with_tesseract(image_path)
                    if text and len(text.strip()) > 10:
                        logger.info("✅ Tesseract OCR successful")
                        return text
                    else:
                        logger.info("Tesseract returned minimal text, trying fallback methods")
                except Exception as e:
                    logger.warning(f"Tesseract OCR failed: {e}")
            else:
                logger.info("Tesseract not available, using fallback methods")
            
            # Метод 2: LLM Vision (fallback)
            if self.llm_vision_available or user_providers:
                try:
                    text = await self.extract_text_with_llm_vision(image_path, user_providers)
                    if text and len(text.strip()) > 20:
                        logger.info("✅ LLM Vision OCR successful")
                        return text
                    else:
                        logger.info("LLM Vision returned minimal text, trying other fallback methods")
                except Exception as e:
                    logger.warning(f"LLM Vision OCR failed: {e}")
            else:
                logger.info("LLM Vision not available, trying online OCR")
            
            # Метод 3: OCR.space API
            if self.ocr_space_available:
                try:
                    text = await self.extract_text_with_ocr_space(image_path)
                    if text and len(text.strip()) > 10:
                        logger.info("✅ OCR.space API successful")
                        return text
                except Exception as e:
                    logger.warning(f"OCR.space API failed: {e}")
            
            # Метод 4: Azure Computer Vision
            if self.azure_vision_available:
                try:
                    text = await self.extract_text_with_azure_vision(image_path)
                    if text and len(text.strip()) > 10:
                        logger.info("✅ Azure Vision API successful")
                        return text
                except Exception as e:
                    logger.warning(f"Azure Vision API failed: {e}")
            
            # Метод 5: Последний fallback - передать изображение в LLM с базовым запросом
            if (self.llm_vision_available or user_providers):
                try:
                    logger.info("Trying LLM Vision fallback with simple prompt")
                    simple_prompt = "Извлеките весь текст из этого изображения. Отвечайте только текстом, который видите."
                    if user_providers:
                        for provider_type, model_name, api_key in user_providers:
                            try:
                                provider = modern_llm_manager.create_user_provider(provider_type, model_name, api_key)
                                result = await provider.generate_content(simple_prompt, image_path)
                                if result and len(result.strip()) > 5:
                                    logger.info("✅ LLM Vision fallback successful")
                                    return result.strip()
                            except Exception as e:
                                logger.warning(f"LLM Vision fallback failed for {provider_type}: {e}")
                                continue
                    else:
                        # Пробуем системные провайдеры
                        try:
                            result, provider_name = await modern_llm_manager.generate_content(simple_prompt, image_path)
                            if result and len(result.strip()) > 5:
                                logger.info(f"✅ LLM Vision fallback successful with {provider_name}")
                                return result.strip()
                        except Exception as e:
                            logger.warning(f"System LLM Vision fallback failed: {e}")
                except Exception as e:
                    logger.warning(f"LLM Vision fallback completely failed: {e}")
            
            logger.warning("❌ All OCR methods failed for meaningful text extraction")
            return "Не удалось извлечь текст из изображения. Попробуйте изображение лучшего качества."
            
        except Exception as e:
            logger.error(f"Image OCR completely failed: {e}")
            return "Ошибка при обработке изображения"
    
    async def extract_text_from_pdf(self, pdf_path: str, user_providers: List = None) -> str:
        """
        Извлечение текста из PDF с использованием нескольких методов
        """
        try:
            logger.info(f"Starting PDF OCR for: {pdf_path}")
            
            # Метод 1: Прямое извлечение текста из PDF
            direct_text = self.extract_text_from_pdf_direct(pdf_path)
            if direct_text and len(direct_text.strip()) > 50:
                logger.info("✅ Direct PDF text extraction successful")
                return direct_text
            
            # Метод 2: Конвертация PDF в изображения и OCR
            logger.info("Direct PDF extraction failed, converting to images...")
            
            try:
                # Конвертируем PDF в изображения (ограничиваем 5 страницами)
                images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=5)
                
                extracted_text = ""
                for i, image in enumerate(images):
                    # Сохраняем изображение во временный файл
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                        image.save(temp_img.name, 'PNG')
                        temp_img_path = temp_img.name
                    
                    try:
                        # Извлекаем текст из изображения страницы
                        page_text = await self.extract_text_from_image(temp_img_path, user_providers)
                        if page_text and len(page_text.strip()) > 10:
                            extracted_text += f"--- Страница {i+1} ---\n{page_text}\n\n"
                    finally:
                        # Удаляем временный файл
                        if os.path.exists(temp_img_path):
                            os.unlink(temp_img_path)
                
                if extracted_text.strip():
                    logger.info(f"✅ PDF OCR successful: {len(extracted_text)} characters")
                    return extracted_text.strip()
                
            except Exception as e:
                logger.error(f"PDF to images conversion failed: {e}")
            
            logger.warning("❌ All PDF OCR methods failed")
            return "PDF содержит изображения, но не удалось извлечь текст"
            
        except Exception as e:
            logger.error(f"PDF OCR completely failed: {e}")
            return "Ошибка при обработке PDF файла"
    
    async def process_document(self, file_path: str, file_type: str, user_providers: List = None) -> Tuple[str, str]:
        """
        Основной метод обработки документов
        """
        try:
            logger.info(f"Processing document: {file_path}, type: {file_type}")
            
            extracted_text = ""
            processing_method = "unknown"
            
            # Определяем тип файла и выбираем метод обработки
            if file_type.lower() == 'pdf' or file_path.lower().endswith('.pdf'):
                extracted_text = await self.extract_text_from_pdf(file_path, user_providers)
                processing_method = "improved_pdf_ocr"
                
            elif file_type.startswith('image/') or any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']):
                extracted_text = await self.extract_text_from_image(file_path, user_providers)
                processing_method = "improved_image_ocr"
                
            else:
                # Пробуем как текстовый файл
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                    processing_method = "text_file"
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='cp1252') as f:
                            extracted_text = f.read()
                        processing_method = "text_file_cp1252"
                    except Exception as e:
                        logger.error(f"Text file reading failed: {e}")
                        extracted_text = "Не удалось распознать тип файла или извлечь текст"
                        processing_method = "error"
            
            # Проверяем качество извлеченного текста
            if extracted_text and len(extracted_text.strip()) > 10:
                logger.info(f"✅ Document processing successful: {processing_method}, {len(extracted_text)} characters")
            else:
                logger.warning(f"⚠️ Document processing returned minimal text: {processing_method}")
            
            return extracted_text, processing_method
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return "Ошибка при обработке документа", "error"
    
    def get_service_status(self) -> dict:
        """Получение статуса сервиса"""
        return {
            "service_name": "Improved OCR Service",
            "methods": {
                "llm_vision": {
                    "available": self.llm_vision_available,
                    "description": "LLM Vision (Gemini Pro Vision, GPT-4V, Claude 3.5 Sonnet)"
                },
                "ocr_space": {
                    "available": self.ocr_space_available,
                    "description": "OCR.space API (бесплатный лимит)"
                },
                "azure_vision": {
                    "available": self.azure_vision_available,
                    "description": "Azure Computer Vision API"
                },
                "direct_pdf": {
                    "available": True,
                    "description": "Прямое извлечение текста из PDF"
                }
            },
            "primary_method": "llm_vision" if self.llm_vision_available else "ocr_space",
            "tesseract_dependency": False,
            "production_ready": True
        }

# Глобальный экземпляр улучшенного OCR сервиса
improved_ocr_service = ImprovedOCRService()