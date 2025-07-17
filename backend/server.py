from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta
import jwt
import json
import tempfile
import shutil
import asyncio
from google.auth.transport import requests
from google.oauth2 import id_token

# Load database and LLM Manager
from database import db
from llm_manager import llm_manager
from modern_llm_manager import modern_llm_manager
from telegram_service import telegram_service
from text_formatter import format_analysis_text, create_improved_analysis_prompt
from google_api_key_service import google_api_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Google OAuth settings
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# Create the main app
app = FastAPI(
    title="German Letter AI Assistant API",
    description="Backend API for German Letter AI Assistant - Google OAuth and AI Document Analysis (SQLite)",
    version="3.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# HTTP Bearer for JWT
security = HTTPBearer()

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class GoogleOAuthUser(BaseModel):
    email: EmailStr
    name: str
    google_id: str
    picture: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    oauth_provider: str
    created_at: datetime
    last_login: Optional[datetime] = None
    has_gemini_api_key: bool = False
    has_openai_api_key: bool = False
    has_anthropic_api_key: bool = False

class ApiKeyUpdate(BaseModel):
    # Новые названия (приоритет)
    api_key_1: Optional[str] = None
    api_key_2: Optional[str] = None
    api_key_3: Optional[str] = None
    # Старые названия (для обратной совместимости)
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

class QuickGeminiSetup(BaseModel):
    api_key: str

class GoogleAuthRequest(BaseModel):
    credential: str

class DocumentAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    file_name: str
    file_type: str
    analysis_result: Dict[str, Any]
    analysis_language: str
    llm_provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Root endpoint (без префикса)
@app.get("/")
async def read_root():
    return {
        "message": "German Letter AI Assistant Backend v3.0", 
        "status": "OK", 
        "auth": "Google OAuth Only", 
        "database": "SQLite",
        "version": "3.0.0"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "german-letter-ai-assistant", 
        "auth": "google-oauth-only",
        "database": "sqlite"
    }

# API endpoints (с префиксом /api)
@api_router.get("/")
async def api_root():
    return {
        "message": "German Letter AI Assistant API v3.0", 
        "status": "Running", 
        "auth": "Google OAuth Only",
        "database": "SQLite"
    }

class AppTextUpdate(BaseModel):
    text_value: str
    description: Optional[str] = None

class AppTextCreate(BaseModel):
    key_name: str
    text_value: str
    description: Optional[str] = None
    category: str = 'general'

class AdminAuth(BaseModel):
    password: str

# Простая админская авторизация
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def verify_admin_password(password: str) -> bool:
    return password == ADMIN_PASSWORD

# Health check endpoint
@api_router.get("/health")
async def health_check():
    try:
        users_count = await db.get_users_count()
        analyses_count = await db.get_analyses_count()
        return {
            "status": "healthy",
            "database": "connected",
            "users_count": users_count,
            "analyses_count": analyses_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Legacy status endpoints (for compatibility)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.save_status_check(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.get_status_checks()
    return [StatusCheck(**status_check) for status_check in status_checks]

# Google OAuth verification (REQUIRED - no skip functionality)
@api_router.post("/auth/google/verify")
async def verify_google_token(auth_request: GoogleAuthRequest):
    try:
        # Verify the Google ID token
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        try:
            idinfo = id_token.verify_oauth2_token(
                auth_request.credential,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            # Verify the token was issued by Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

        # Extract user info from verified token
        user_info = {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture')
        }

        # Create or get user
        user_id = f"google_{user_info['sub']}"
        existing_user = await db.get_user(user_id)

        if existing_user:
            # Update existing user
            existing_user["last_login"] = datetime.utcnow().isoformat()
            await db.save_user(existing_user)
            user = existing_user
        else:
            # Create new user
            user = {
                "id": user_id,
                "email": user_info["email"],
                "name": user_info["name"],
                "picture": user_info.get("picture"),
                "oauth_provider": "Google",
                "google_id": user_info["sub"],
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "gemini_api_key": None,
                "openai_api_key": None,
                "anthropic_api_key": None
            }
            await db.save_user(user)

        # Create access token
        access_token = create_access_token({"sub": user_id, "email": user["email"]})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
                "oauth_provider": user["oauth_provider"],
                "has_gemini_api_key": bool(user.get("gemini_api_key")),
                "has_openai_api_key": bool(user.get("openai_api_key")),
                "has_anthropic_api_key": bool(user.get("anthropic_api_key"))
            }
        }
    except Exception as e:
        logger.error(f"Google OAuth verification failed: {e}")
        raise HTTPException(status_code=400, detail="Google authentication failed")

# User profile (REQUIRES AUTHENTICATION)
@api_router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        picture=current_user.get("picture"),
        oauth_provider=current_user["oauth_provider"],
        created_at=datetime.fromisoformat(current_user["created_at"]),
        last_login=datetime.fromisoformat(current_user["last_login"]) if current_user.get("last_login") else None,
        has_gemini_api_key=bool(current_user.get("gemini_api_key")),
        has_openai_api_key=bool(current_user.get("openai_api_key")),
        has_anthropic_api_key=bool(current_user.get("anthropic_api_key"))
    )

# Save API keys (REQUIRES AUTHENTICATION)
@api_router.post("/api-keys")
async def save_api_keys(
    api_key_data: ApiKeyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        updated_keys = []
        
        # Map new field names to old field names for processing
        # Priority: new names override old names
        gemini_key = api_key_data.api_key_1 or api_key_data.gemini_api_key
        openai_key = api_key_data.api_key_2 or api_key_data.openai_api_key  
        anthropic_key = api_key_data.api_key_3 or api_key_data.anthropic_api_key
        
        # Update Gemini API key if provided (api_key_1 or gemini_api_key)
        if gemini_key:
            try:
                test_provider = llm_manager.create_user_provider("gemini", "gemini-1.5-flash", gemini_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["gemini_api_key"] = gemini_key
                    updated_keys.append("API Key 1 (Gemini)")
            except Exception as e:
                logger.error(f"Invalid API Key 1 (Gemini): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 1")

        # Update OpenAI API key if provided (api_key_2 or openai_api_key)
        if openai_key:
            try:
                test_provider = llm_manager.create_user_provider("openai", "gpt-4o-mini", openai_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["openai_api_key"] = openai_key
                    updated_keys.append("API Key 2 (OpenAI)")
            except Exception as e:
                logger.error(f"Invalid API Key 2 (OpenAI): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 2")

        # Update Anthropic API key if provided (api_key_3 or anthropic_api_key)
        if anthropic_key:
            try:
                test_provider = llm_manager.create_user_provider("anthropic", "claude-3-haiku-20240307", anthropic_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["anthropic_api_key"] = anthropic_key
                    updated_keys.append("API Key 3 (Anthropic)")
            except Exception as e:
                logger.error(f"Invalid API Key 3 (Anthropic): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 3")

        # Save updated user data
        await db.save_user(current_user)

        return {
            "message": f"API ключи успешно обновлены: {', '.join(updated_keys)}", 
            "status": "success",
            "updated_keys": updated_keys
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API keys")

# Auto-generate Gemini API key (REQUIRES AUTHENTICATION)
@api_router.post("/auto-generate-gemini-key")
async def auto_generate_gemini_key(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Автоматически создать и сохранить Gemini API ключ для пользователя"""
    try:
        user_id = str(current_user.get("id", ""))
        user_email = current_user.get("email", "")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Email пользователя не найден")
        
        # Проверяем, есть ли уже Gemini ключ
        existing_key = current_user.get("gemini_api_key")
        if existing_key:
            # Проверяем валидность существующего ключа
            is_valid = await google_api_service.validate_api_key(existing_key)
            if is_valid:
                return {
                    "message": "У вас уже есть действующий Gemini API ключ!",
                    "status": "existing",
                    "api_key_masked": f"{existing_key[:8]}...{existing_key[-4:]}",
                    "provider": "Gemini"
                }
        
        # Создаем новый API ключ
        logger.info(f"Creating Gemini API key for user {user_email}")
        key_result = await google_api_service.create_gemini_api_key(user_id, user_email)
        
        # Валидируем созданный ключ
        is_valid = await google_api_service.validate_api_key(key_result["api_key"])
        if not is_valid:
            logger.warning(f"Generated API key validation failed for user {user_email}")
            # Все равно сохраняем демо ключ для тестирования
        
        # Сохраняем API ключ в профиле пользователя
        current_user["gemini_api_key"] = key_result["api_key"]
        await db.save_user(current_user)
        
        logger.info(f"Successfully generated and saved Gemini API key for user {user_email}")
        
        return {
            "message": key_result["message"],
            "status": key_result["status"],
            "api_key_masked": f"{key_result['api_key'][:8]}...{key_result['api_key'][-4:]}",
            "provider": "Gemini",
            "display_name": key_result.get("display_name", ""),
            "restrictions": key_result.get("restrictions", {}),
            "auto_generated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to auto-generate Gemini API key: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при автоматическом создании API ключа: {str(e)}"
        )

# Quick Gemini setup (REQUIRES AUTHENTICATION)
@api_router.post("/quick-gemini-setup")
async def quick_gemini_setup(
    gemini_data: QuickGeminiSetup,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Test the API key with modern manager
        is_valid = await modern_llm_manager.test_api_key("gemini", gemini_data.api_key)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Недействительный Gemini API ключ")
        
        # Save the API key
        current_user["gemini_api_key"] = gemini_data.api_key
        await db.save_user(current_user)
        
        return {
            "message": "Gemini API успешно подключен! Теперь вы можете использовать полную функциональность приложения.",
            "status": "success",
            "provider": "Gemini",
            "model": "gemini-2.0-flash"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to setup Gemini API: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при настройке Gemini API")

# Get modern LLM providers status
@api_router.get("/modern-llm-status")
async def get_modern_llm_status():
    try:
        provider_status = modern_llm_manager.get_provider_status()
        active_count = sum(1 for status in provider_status.values() if status["status"] == "active")
        return {
            "status": "success",
            "providers": provider_status,
            "active_providers": active_count,
            "total_providers": len(provider_status),
            "modern": True
        }
    except Exception as e:
        logger.error(f"Failed to get modern LLM status: {e}")
        return {"status": "error", "message": str(e), "modern": True}

# Get LLM providers status
@api_router.get("/llm-status")
async def get_llm_status():
    try:
        provider_status = llm_manager.get_provider_status()
        active_count = sum(1 for status in provider_status.values() if status["status"] == "active")
        return {
            "status": "success",
            "providers": provider_status,
            "active_providers": active_count,
            "total_providers": len(provider_status)
        }
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        return {"status": "error", "message": str(e)}

# Analyze file with user's API keys (REQUIRES AUTHENTICATION)
@api_router.post("/analyze-file")
async def analyze_file_authenticated(
    file: UploadFile = File(...),
    language: str = Form("en"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Check if user has at least one API key
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-1.5-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))

        if not user_providers:
            # Try system providers if no user keys
            active_providers = llm_manager.get_available_providers()
            if not any(active_providers.values()):
                raise HTTPException(
                    status_code=400,
                    detail="No API keys configured. Please add your API keys in profile."
                )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        try:
            # Create improved analysis prompt
            analysis_prompt = create_improved_analysis_prompt(language, file.filename)

            # Check if file is an image
            is_image = file.content_type and file.content_type.startswith('image/')

            # Try user providers first with modern manager
            response_text = None
            provider_used = None
            
            if user_providers:
                for provider_type, model_name, api_key in user_providers:
                    try:
                        # Use modern manager for Gemini
                        if provider_type == "gemini":
                            user_provider = modern_llm_manager.create_user_provider(provider_type, "gemini-2.0-flash", api_key)
                        else:
                            user_provider = llm_manager.create_user_provider(provider_type, model_name, api_key)
                        
                        response_text = await user_provider.generate_content(
                            analysis_prompt,
                            temp_file_path if is_image else None
                        )
                        provider_used = f"{provider_type.title()} (User API Key)"
                        break
                    except Exception as e:
                        logger.warning(f"User provider {provider_type} failed: {e}")
                        continue

            # If no user providers worked, try system providers
            if not response_text:
                response_text, system_provider = await llm_manager.generate_content(
                    analysis_prompt,
                    temp_file_path if is_image else None
                )
                provider_used = f"{system_provider} (System)"

            # Format the response text using our formatter
            formatted_analysis = format_analysis_text(response_text)
            
            # Structure the response
            analysis_result = {
                "summary": f"Анализ файла {file.filename} выполнен успешно",
                "analysis": {
                    "sender": formatted_analysis.get("sender_info", "Не указан"),
                    "letter_type": formatted_analysis.get("document_type", "Официальный документ"),
                    "main_content": formatted_analysis.get("main_content", response_text[:500] + "..." if len(response_text) > 500 else response_text),
                    "full_analysis": formatted_analysis.get("full_analysis", response_text),
                    "key_content": formatted_analysis.get("key_content", ""),
                    "required_actions": formatted_analysis.get("required_actions", ""),
                    "deadlines": formatted_analysis.get("deadlines", ""),
                    "consequences": formatted_analysis.get("consequences", ""),
                    "formatted_sections": formatted_analysis.get("formatted_sections", [])
                },
                "actions_needed": [
                    "Изучить содержание документа",
                    "Предпринять соответствующие действия согласно требованиям"
                ],
                "urgency_level": formatted_analysis.get("urgency_level", "СРЕДНИЙ"),
                "response_template": formatted_analysis.get("response_template", "Спасибо за ваше письмо. Мы изучим и ответим соответствующим образом."),
                "llm_provider": provider_used,
                "file_name": file.filename,
                "analysis_language": language,
                "file_type": "image" if is_image else "document"
            }

            # Save analysis to database
            doc_analysis = {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "file_name": file.filename,
                "file_type": "image" if is_image else "document",
                "analysis_result": analysis_result,
                "analysis_language": language,
                "llm_provider": provider_used
            }
            await db.save_analysis(doc_analysis)

            return analysis_result

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Get user's analysis history (REQUIRES AUTHENTICATION)
@api_router.get("/analysis-history")
async def get_analysis_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        analyses = await db.get_user_analyses(current_user["id"])
        return {
            "status": "success",
            "count": len(analyses),
            "analyses": analyses
        }
    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis history")

# Get Telegram news (PUBLIC ENDPOINT)
@api_router.get("/telegram-news")
async def get_telegram_news(limit: int = 5):
    """Получить последние новости из Telegram канала"""
    try:
        # Пробуем получить реальные новости
        news = await telegram_service.get_channel_posts(limit=limit)
        
        # Если не получилось, возвращаем демо-новости
        if not news:
            news = await telegram_service.get_sample_news()
        
        return {
            "status": "success",
            "count": len(news),
            "news": news,
            "channel_name": telegram_service.channel_name,
            "channel_link": f"https://t.me/{telegram_service.channel_name}"
        }
    except Exception as e:
        logger.error(f"Failed to get Telegram news: {e}")
        # В случае ошибки возвращаем демо-новости
        demo_news = await telegram_service.get_sample_news()
        return {
            "status": "demo",
            "count": len(demo_news),
            "news": demo_news,
            "channel_name": telegram_service.channel_name,
            "channel_link": f"https://t.me/{telegram_service.channel_name}",
            "note": "Демо-режим: показаны примерные новости"
        }

# =============== ADMIN API ENDPOINTS ===============

# Admin login
@api_router.post("/admin/login")
async def admin_login(admin_auth: AdminAuth):
    """Админская авторизация"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    return {
        "status": "success",
        "message": "Успешная авторизация",
        "is_admin": True
    }

# Get all app texts
@api_router.post("/admin/texts")
async def get_admin_texts(admin_auth: AdminAuth):
    """Получить все тексты приложения (только для админа)"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        texts = await db.get_app_texts_by_category()
        return {
            "status": "success",
            "texts": texts
        }
    except Exception as e:
        logger.error(f"Failed to get app texts: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения текстов")

# Update app text
@api_router.put("/admin/texts/{key_name}")
async def update_admin_text(key_name: str, admin_auth: AdminAuth, text_update: AppTextUpdate):
    """Обновить текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.update_app_text(key_name, text_update.text_value, text_update.description)
        if success:
            return {
                "status": "success",
                "message": f"Текст '{key_name}' обновлен"
            }
        else:
            raise HTTPException(status_code=404, detail="Текст не найден")
    except Exception as e:
        logger.error(f"Failed to update app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обновления текста")

# Create new app text
@api_router.post("/admin/texts/create")
async def create_admin_text(admin_auth: AdminAuth, text_create: AppTextCreate):
    """Создать новый текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.create_app_text(
            text_create.key_name,
            text_create.text_value,
            text_create.description,
            text_create.category
        )
        if success:
            return {
                "status": "success",
                "message": f"Текст '{text_create.key_name}' создан"
            }
        else:
            raise HTTPException(status_code=400, detail="Ошибка создания текста")
    except Exception as e:
        logger.error(f"Failed to create app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания текста")

# Delete app text
@api_router.delete("/admin/texts/{key_name}")
async def delete_admin_text(key_name: str, admin_auth: AdminAuth):
    """Удалить текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.delete_app_text(key_name)
        if success:
            return {
                "status": "success",
                "message": f"Текст '{key_name}' удален"
            }
        else:
            raise HTTPException(status_code=404, detail="Текст не найден")
    except Exception as e:
        logger.error(f"Failed to delete app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка удаления текста")

# Get public app texts (for frontend)
@api_router.get("/texts")
async def get_public_texts():
    """Получить тексты приложения для фронтенда"""
    try:
        texts = await db.get_app_texts()
        texts_dict = {}
        for text in texts:
            texts_dict[text['key_name']] = text['text_value']
        
        return {
            "status": "success",
            "texts": texts_dict
        }
    except Exception as e:
        logger.error(f"Failed to get public texts: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения текстов")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
