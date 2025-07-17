import os
import asyncio
import logging
import mimetypes
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType, ImageContent
import tempfile
import base64
from PIL import Image
import google.generativeai as genai
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ModernLLMProvider(ABC):
    """Абстрактный класс для современных провайдеров LLM"""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.name = self.__class__.__name__

    @abstractmethod
    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        """Генерация контента с опциональным изображением"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Проверка доступности провайдера"""
        pass

class ModernGeminiProvider(ModernLLMProvider):
    """Современный провайдер для Google Gemini через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        super().__init__(api_key, model_name)
        self.session_id = f"gemini_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.api_key:
                raise Exception("Gemini API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a helpful assistant for analyzing German official letters."
            ).with_model("gemini", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение
            if image_path:
                # Определяем MIME тип изображения
                mime_type, _ = mimetypes.guess_type(image_path)
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = 'image/jpeg'  # по умолчанию
                
                # Добавляем изображение к сообщению
                image_file = FileContentWithMimeType(
                    file_path=image_path,
                    mime_type=mime_type
                )
                user_message = UserMessage(
                    text=prompt,
                    file_contents=[image_file]
                )

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            return response

        except Exception as e:
            logger.error(f"Modern Gemini generation error: {e}")
            raise Exception(f"Gemini error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernOpenAIProvider(ModernLLMProvider):
    """Современный провайдер для OpenAI через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        super().__init__(api_key, model_name)
        self.session_id = f"openai_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.api_key:
                raise Exception("OpenAI API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a helpful assistant for analyzing German official letters."
            ).with_model("openai", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение (используем base64 для OpenAI)
            if image_path:
                # Конвертируем изображение в base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode()
                
                # Добавляем изображение к сообщению
                image_content = ImageContent(image_base64=base64_image)
                user_message = UserMessage(
                    text=prompt,
                    file_contents=[image_content]
                )

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            return response

        except Exception as e:
            logger.error(f"Modern OpenAI generation error: {e}")
            raise Exception(f"OpenAI error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernAnthropicProvider(ModernLLMProvider):
    """Современный провайдер для Anthropic через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model_name)
        self.session_id = f"anthropic_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.api_key:
                raise Exception("Anthropic API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a helpful assistant for analyzing German official letters."
            ).with_model("anthropic", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение (используем base64 для Anthropic)
            if image_path:
                # Конвертируем изображение в base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode()
                
                # Добавляем изображение к сообщению
                image_content = ImageContent(image_base64=base64_image)
                user_message = UserMessage(
                    text=prompt,
                    file_contents=[image_content]
                )

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            return response

        except Exception as e:
            logger.error(f"Modern Anthropic generation error: {e}")
            raise Exception(f"Anthropic error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernLLMManager:
    """Современный менеджер для управления различными провайдерами LLM"""

    def __init__(self):
        self.providers: Dict[str, ModernLLMProvider] = {}
        self.initialize_providers()

    def initialize_providers(self):
        """Инициализация провайдеров на основе переменных окружения"""
        try:
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY')
            if gemini_key:
                self.providers['gemini'] = ModernGeminiProvider(gemini_key)

            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                self.providers['openai'] = ModernOpenAIProvider(openai_key)

            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.providers['anthropic'] = ModernAnthropicProvider(anthropic_key)

            logger.info(f"Modern LLM Manager initialized with {len(self.providers)} providers")
        except Exception as e:
            logger.error(f"Failed to initialize modern providers: {e}")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Получение статуса всех провайдеров"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "status": "active" if provider.is_available() else "inactive",
                "model": provider.model_name,
                "name": provider.name,
                "modern": True
            }

        # Добавляем провайдеры без ключей
        all_providers = ['gemini', 'openai', 'anthropic']
        for provider_name in all_providers:
            if provider_name not in status:
                status[provider_name] = {
                    "status": "inactive",
                    "model": "N/A",
                    "name": f"Modern{provider_name.title()}Provider",
                    "modern": True
                }

        return status

    def create_user_provider(self, provider_type: str, model_name: str, api_key: str) -> ModernLLMProvider:
        """Создание пользовательского провайдера с конкретным API ключом"""
        if provider_type.lower() == 'gemini':
            return ModernGeminiProvider(api_key, model_name)
        elif provider_type.lower() == 'openai':
            return ModernOpenAIProvider(api_key, model_name)
        elif provider_type.lower() == 'anthropic':
            return ModernAnthropicProvider(api_key, model_name)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    async def test_api_key(self, provider_type: str, api_key: str) -> bool:
        """Тестирование API ключа"""
        try:
            if provider_type.lower() == 'gemini':
                provider = ModernGeminiProvider(api_key)
            elif provider_type.lower() == 'openai':
                provider = ModernOpenAIProvider(api_key)
            elif provider_type.lower() == 'anthropic':
                provider = ModernAnthropicProvider(api_key)
            else:
                return False

            # Тестируем с простым сообщением
            response = await provider.generate_content("Test message")
            return bool(response)
        except Exception as e:
            logger.error(f"API key test failed for {provider_type}: {e}")
            return False

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> Tuple[str, str]:
        """Генерация контента с автоматическим выбором провайдера"""
        active_providers = [name for name, provider in self.providers.items() if provider.is_available()]

        if not active_providers:
            return "Демо анализ: Это тестовый ответ. Пожалуйста, настройте API ключи для полной функциональности.", "Demo"

        # Попробуем провайдеры в порядке приоритета
        priority_order = ['gemini', 'openai', 'anthropic']

        for provider_name in priority_order:
            if provider_name in active_providers:
                try:
                    provider = self.providers[provider_name]
                    response = await provider.generate_content(prompt, image_path)
                    return response, f"{provider_name.title()} (Modern)"
                except Exception as e:
                    logger.warning(f"Modern provider {provider_name} failed: {e}")
                    continue

        return "Ошибка: Все современные LLM провайдеры недоступны. Проверьте API ключи.", "Error"

    def get_available_providers(self) -> Dict[str, bool]:
        """Получение списка доступных провайдеров"""
        return {name: provider.is_available() for name, provider in self.providers.items()}

# Глобальный экземпляр современного менеджера
modern_llm_manager = ModernLLMManager()