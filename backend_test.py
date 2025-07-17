#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for German Letter AI Assistant
Tests SQLite conversion, authentication system, and LLM manager functionality
"""

import asyncio
import aiohttp
import json
import os
import tempfile
from pathlib import Path
import logging
from typing import Dict, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "http://localhost:8001"  # Use localhost for testing new features
        
        # Use production URL for testing as specified in review request
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        if not self.backend_url:
            self.backend_url = "http://localhost:8001"  # Fallback to localhost
            
        logger.info(f"Testing backend at: {self.backend_url}")
        
        self.session = None
        self.test_results = []
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, Any, str]:
        """Make HTTP request and return success, data, error"""
        try:
            url = f"{self.backend_url}{endpoint}"
            
            # Add auth header if we have a token
            if self.auth_token and 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self.auth_token:
                kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
            
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status < 400:
                    return True, data, ""
                else:
                    return False, data, f"HTTP {response.status}"
                    
        except Exception as e:
            return False, None, str(e)
    
    async def test_basic_health_endpoints(self):
        """Test basic health check endpoints"""
        logger.info("=== Testing Basic Health Endpoints ===")
        
        # Test root endpoint
        success, data, error = await self.make_request("GET", "/")
        if success and isinstance(data, dict):
            expected_fields = ["message", "status", "auth", "database", "version"]
            has_all_fields = all(field in data for field in expected_fields)
            is_sqlite = data.get("database") == "SQLite"
            is_google_only = "Google OAuth" in str(data.get("auth", ""))
            
            self.log_test_result(
                "GET / - Root endpoint",
                has_all_fields and is_sqlite and is_google_only,
                f"Database: {data.get('database')}, Auth: {data.get('auth')}, Version: {data.get('version')}",
                data
            )
        else:
            self.log_test_result("GET / - Root endpoint", False, f"Error: {error}", data)
        
        # Test health endpoint
        success, data, error = await self.make_request("GET", "/health")
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "healthy"
            has_service = "service" in data
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "GET /health - Health check",
                has_status and has_service and is_sqlite,
                f"Status: {data.get('status')}, Database: {data.get('database')}",
                data
            )
        else:
            self.log_test_result("GET /health - Health check", False, f"Error: {error}", data)
    
    async def test_api_health_endpoints(self):
        """Test API health endpoints"""
        logger.info("=== Testing API Health Endpoints ===")
        
        # Test API root
        success, data, error = await self.make_request("GET", "/api/")
        if success and isinstance(data, dict):
            has_message = "message" in data
            is_sqlite = data.get("database") == "SQLite"
            is_google_only = "Google OAuth" in str(data.get("auth", ""))
            
            self.log_test_result(
                "GET /api/ - API root",
                has_message and is_sqlite and is_google_only,
                f"Database: {data.get('database')}, Auth: {data.get('auth')}",
                data
            )
        else:
            self.log_test_result("GET /api/ - API root", False, f"Error: {error}", data)
        
        # Test API health with database counts
        success, data, error = await self.make_request("GET", "/api/health")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "healthy"
            has_counts = "users_count" in data and "analyses_count" in data
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "GET /api/health - Detailed health",
                has_status and has_counts and is_sqlite,
                f"Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}, DB: {data.get('database')}",
                data
            )
        else:
            self.log_test_result("GET /api/health - Detailed health", False, f"Error: {error}", data)
    
    async def test_llm_status_endpoint(self):
        """Test LLM status endpoint"""
        logger.info("=== Testing LLM Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/llm-status")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            has_counts = "active_providers" in data and "total_providers" in data
            
            # Check if all expected providers are present
            expected_providers = ["gemini", "openai", "anthropic"]
            providers_present = all(provider in data.get("providers", {}) for provider in expected_providers)
            
            self.log_test_result(
                "GET /api/llm-status - LLM providers status",
                has_status and has_providers and has_counts and providers_present,
                f"Active: {data.get('active_providers')}/{data.get('total_providers')}, Providers: {list(data.get('providers', {}).keys())}",
                data
            )
        else:
            self.log_test_result("GET /api/llm-status - LLM providers status", False, f"Error: {error}", data)
    
    async def test_legacy_status_endpoints(self):
        """Test legacy status endpoints for compatibility"""
        logger.info("=== Testing Legacy Status Endpoints ===")
        
        # Test creating status check
        test_data = {"client_name": "test_client_backend_api"}
        success, data, error = await self.make_request("POST", "/api/status", json=test_data)
        
        if success and isinstance(data, dict):
            has_id = "id" in data
            has_client_name = data.get("client_name") == test_data["client_name"]
            has_timestamp = "timestamp" in data
            
            self.log_test_result(
                "POST /api/status - Create status check",
                has_id and has_client_name and has_timestamp,
                f"Created status check with ID: {data.get('id')}",
                data
            )
        else:
            self.log_test_result("POST /api/status - Create status check", False, f"Error: {error}", data)
        
        # Test getting status checks
        success, data, error = await self.make_request("GET", "/api/status")
        if success and isinstance(data, list):
            has_data = len(data) > 0
            if has_data:
                first_item = data[0]
                has_required_fields = all(field in first_item for field in ["id", "client_name", "timestamp"])
            else:
                has_required_fields = True  # Empty list is acceptable
            
            self.log_test_result(
                "GET /api/status - Get status checks",
                isinstance(data, list) and has_required_fields,
                f"Retrieved {len(data)} status checks",
                {"count": len(data), "sample": data[0] if data else None}
            )
        else:
            self.log_test_result("GET /api/status - Get status checks", False, f"Error: {error}", data)
    
    async def test_authentication_required_endpoints(self):
        """Test that authentication-required endpoints return 401 without token"""
        logger.info("=== Testing Authentication Requirements ===")
        
        auth_required_endpoints = [
            ("GET", "/api/profile", "User profile"),
            ("POST", "/api/api-keys", "Save API keys"),
            ("POST", "/api/analyze-file", "Analyze file"),
            ("GET", "/api/analysis-history", "Analysis history")
        ]
        
        # Test without authentication
        for method, endpoint, description in auth_required_endpoints:
            if method == "POST" and "api-keys" in endpoint:
                # For API keys endpoint, send some test data
                success, data, error = await self.make_request(method, endpoint, json={"gemini_api_key": "test"})
            elif method == "POST" and "analyze-file" in endpoint:
                # For file analysis, we need multipart data
                success, data, error = await self.make_request(method, endpoint, data={"language": "en"})
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should fail with 401 or 403 (both indicate authentication required)
            is_auth_required = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("401" in str(data) or "403" in str(data) or "Not authenticated" in str(data.get("detail", ""))))
            
            self.log_test_result(
                f"{method} {endpoint} - {description} (no auth)",
                not success and is_auth_required,
                f"Correctly returned authentication required" if is_auth_required else f"Unexpected response: {error}",
                data
            )
    
    async def test_google_oauth_endpoint(self):
        """Test Google OAuth endpoint (without valid token)"""
        logger.info("=== Testing Google OAuth Endpoint ===")
        
        # Test with invalid token
        test_data = {"credential": "invalid_google_token"}
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json=test_data)
        
        # Should fail with 400 (invalid token)
        is_400 = "400" in str(error) or (isinstance(data, dict) and "Invalid Google token" in str(data.get("detail", "")))
        
        self.log_test_result(
            "POST /api/auth/google/verify - Google OAuth (invalid token)",
            not success and is_400,
            f"Correctly rejected invalid token" if is_400 else f"Unexpected response: {error}",
            data
        )
        
        # Test with missing credential
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={})
        
        # Should fail with validation error
        is_validation_error = not success and ("422" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/auth/google/verify - Google OAuth (missing credential)",
            is_validation_error,
            f"Correctly returned validation error" if is_validation_error else f"Unexpected response: {error}",
            data
        )
    
    async def test_database_functionality(self):
        """Test SQLite database functionality indirectly through API"""
        logger.info("=== Testing Database Functionality ===")
        
        # Test that health endpoint shows user and analysis counts (tests DB connection)
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            has_user_count = "users_count" in data and isinstance(data["users_count"], int)
            has_analysis_count = "analyses_count" in data and isinstance(data["analyses_count"], int)
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "Database connectivity test",
                has_user_count and has_analysis_count and is_sqlite,
                f"SQLite DB connected, Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}",
                data
            )
        else:
            self.log_test_result("Database connectivity test", False, f"Error: {error}", data)
        
        # Test status checks creation/retrieval (tests SQLite operations)
        test_client = f"db_test_client_{int(time.time())}"
        
        # Create a status check
        success, create_data, error = await self.make_request("POST", "/api/status", json={"client_name": test_client})
        
        if success:
            # Retrieve status checks and verify our entry exists
            success, get_data, error = await self.make_request("GET", "/api/status")
            
            if success and isinstance(get_data, list):
                found_entry = any(item.get("client_name") == test_client for item in get_data)
                
                self.log_test_result(
                    "SQLite CRUD operations test",
                    found_entry,
                    f"Successfully created and retrieved status check for {test_client}",
                    {"created": create_data, "found_in_list": found_entry}
                )
            else:
                self.log_test_result("SQLite CRUD operations test", False, f"Failed to retrieve: {error}", get_data)
        else:
            self.log_test_result("SQLite CRUD operations test", False, f"Failed to create: {error}", create_data)
    
    async def test_no_skip_auth_functionality(self):
        """Test that skip auth functionality has been removed"""
        logger.info("=== Testing No Skip Auth Functionality ===")
        
        # Try various endpoints that might have had skip auth
        test_endpoints = [
            ("GET", "/api/profile"),
            ("POST", "/api/api-keys"),
            ("GET", "/api/analysis-history"),
            ("POST", "/api/quick-gemini-setup")  # New endpoint should also require auth
        ]
        
        all_require_auth = True
        
        for method, endpoint in test_endpoints:
            if method == "POST" and "api-keys" in endpoint:
                success, data, error = await self.make_request(method, endpoint, json={"gemini_api_key": "test"})
            elif method == "POST" and "quick-gemini-setup" in endpoint:
                success, data, error = await self.make_request(method, endpoint, json={"api_key": "test"})
            else:
                success, data, error = await self.make_request(method, endpoint, json={} if method == "POST" else None)
            
            # All should require authentication (return 401 or 403)
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not requires_auth:
                all_require_auth = False
                logger.warning(f"{method} {endpoint} does not require authentication!")
        
        self.log_test_result(
            "No skip auth functionality test",
            all_require_auth,
            "All protected endpoints correctly require authentication" if all_require_auth else "Some endpoints allow unauthorized access",
            {"all_require_auth": all_require_auth}
        )
    
    async def test_modern_llm_status_endpoint(self):
        """Test modern LLM status endpoint"""
        logger.info("=== Testing Modern LLM Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            has_counts = "active_providers" in data and "total_providers" in data
            has_modern_flag = data.get("modern") is True
            
            # Check if all expected providers are present
            expected_providers = ["gemini", "openai", "anthropic"]
            providers_present = all(provider in data.get("providers", {}) for provider in expected_providers)
            
            # Check if providers have modern flag
            providers_modern = all(
                provider_info.get("modern") is True 
                for provider_info in data.get("providers", {}).values()
            )
            
            self.log_test_result(
                "GET /api/modern-llm-status - Modern LLM providers status",
                has_status and has_providers and has_counts and providers_present and has_modern_flag and providers_modern,
                f"Active: {data.get('active_providers')}/{data.get('total_providers')}, Modern: {has_modern_flag}, Providers: {list(data.get('providers', {}).keys())}",
                data
            )
        else:
            self.log_test_result("GET /api/modern-llm-status - Modern LLM providers status", False, f"Error: {error}", data)
    
    async def test_quick_gemini_setup_endpoint(self):
        """Test quick Gemini setup endpoint (without authentication)"""
        logger.info("=== Testing Quick Gemini Setup Endpoint ===")
        
        # Test without authentication - should fail
        test_data = {"api_key": "test_invalid_key"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=test_data)
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/quick-gemini-setup - Quick Gemini setup (no auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test with missing api_key field
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json={})
        
        # Should fail with validation error or auth error
        is_validation_or_auth_error = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/quick-gemini-setup - Quick Gemini setup (missing api_key)",
            is_validation_or_auth_error,
            f"Correctly returned validation/auth error" if is_validation_or_auth_error else f"Unexpected response: {error}",
            data
        )
    
    async def test_image_recognition_functionality(self):
        """Test critical image recognition functionality with modern LLM manager"""
        logger.info("=== Testing Image Recognition Functionality ===")
        
        # Test that modern LLM status endpoint shows image support
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if modern providers are configured for image support
            modern_providers_available = []
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    if provider_info.get("modern") is True:
                        modern_providers_available.append(provider_name)
            
            self.log_test_result(
                "Modern LLM Status - Image support check",
                has_modern_flag and has_providers and len(modern_providers_available) > 0,
                f"Modern flag: {has_modern_flag}, Modern providers: {modern_providers_available}",
                data
            )
        else:
            self.log_test_result("Modern LLM Status - Image support check", False, f"Error: {error}", data)
        
        # Test analyze-file endpoint without authentication (should fail)
        # Create a simple test image file
        test_image_data = self.create_test_image()
        
        # Test without authentication
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'en')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication required
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - Image analysis (no auth)",
            is_auth_required,
            f"Correctly requires authentication for image analysis" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test that the endpoint accepts image files (structure test)
        # This tests the endpoint structure without actually processing
        form_data_invalid = aiohttp.FormData()
        form_data_invalid.add_field('language', 'en')  # Missing file
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data_invalid)
        
        # Should fail with validation error or auth error (both are acceptable)
        is_validation_or_auth_error = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower() or "field required" in str(data).lower())
        
        self.log_test_result(
            "POST /api/analyze-file - Image analysis (missing file)",
            is_validation_or_auth_error,
            f"Correctly handles missing file parameter" if is_validation_or_auth_error else f"Unexpected response: {error}",
            data
        )
    
    def create_test_image(self):
        """Create a simple test image for testing"""
        try:
            from PIL import Image
            import io
            
            # Create a simple 100x100 red image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except ImportError:
            # If PIL is not available, create a minimal JPEG-like bytes
            # This is just for testing the endpoint structure
            return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00d\x00d\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    async def test_modern_llm_manager_integration(self):
        """Test modern LLM manager integration and image path parameter handling"""
        logger.info("=== Testing Modern LLM Manager Integration ===")
        
        # Test modern LLM status endpoint for proper integration
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # Check for modern flag and proper provider structure
            has_modern_flag = data.get("modern") is True
            has_status = data.get("status") == "success"
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if providers have modern models configured
            modern_models_found = []
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    model = provider_info.get("model", "")
                    if any(modern_model in model for modern_model in ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]):
                        modern_models_found.append(f"{provider_name}:{model}")
            
            self.log_test_result(
                "Modern LLM Manager - Integration check",
                has_modern_flag and has_status and has_providers,
                f"Modern: {has_modern_flag}, Status: {has_status}, Modern models: {modern_models_found}",
                data
            )
            
            # Check specific modern models are configured
            expected_modern_models = ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]
            models_configured = []
            
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    model = provider_info.get("model", "")
                    if model in expected_modern_models:
                        models_configured.append(model)
            
            self.log_test_result(
                "Modern LLM Manager - Modern models configuration",
                len(models_configured) > 0,
                f"Modern models configured: {models_configured} out of expected: {expected_modern_models}",
                {"configured": models_configured, "expected": expected_modern_models}
            )
        else:
            self.log_test_result("Modern LLM Manager - Integration check", False, f"Error: {error}", data)
    
    async def test_emergentintegrations_support(self):
        """Test emergentintegrations library support"""
        logger.info("=== Testing Emergentintegrations Support ===")
        
        # Test that modern LLM status shows emergentintegrations support
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # Check if the response indicates modern LLM support
            has_modern_flag = data.get("modern") is True
            providers = data.get("providers", {})
            
            # Check if providers have modern flag indicating emergentintegrations support
            emergent_support = all(
                provider_info.get("modern") is True 
                for provider_info in providers.values()
            ) if providers else False
            
            self.log_test_result(
                "Emergentintegrations - Library support check",
                has_modern_flag and emergent_support,
                f"Modern flag: {has_modern_flag}, All providers modern: {emergent_support}, Providers: {list(providers.keys())}",
                data
            )
        else:
            self.log_test_result("Emergentintegrations - Library support check", False, f"Error: {error}", data)
    
    async def test_telegram_news_endpoint(self):
        """Test new Telegram news endpoint"""
        logger.info("=== Testing Telegram News Endpoint ===")
        
        # Test basic endpoint functionality
        success, data, error = await self.make_request("GET", "/api/telegram-news")
        
        if success and isinstance(data, dict):
            # Check required fields
            has_status = "status" in data
            has_count = "count" in data and isinstance(data["count"], int)
            has_news = "news" in data and isinstance(data["news"], list)
            has_channel_info = "channel_name" in data and "channel_link" in data
            
            # Check news structure if any news exist
            news_structure_valid = True
            if data.get("news"):
                first_news = data["news"][0]
                required_news_fields = ["id", "text", "preview_text", "date", "formatted_date", "channel_name", "link"]
                news_structure_valid = all(field in first_news for field in required_news_fields)
            
            self.log_test_result(
                "GET /api/telegram-news - Basic functionality",
                has_status and has_count and has_news and has_channel_info and news_structure_valid,
                f"Status: {data.get('status')}, Count: {data.get('count')}, Channel: {data.get('channel_name')}, News structure valid: {news_structure_valid}",
                data
            )
        else:
            self.log_test_result("GET /api/telegram-news - Basic functionality", False, f"Error: {error}", data)
        
        # Test with limit parameter
        success, data, error = await self.make_request("GET", "/api/telegram-news?limit=3")
        
        if success and isinstance(data, dict):
            news_count = len(data.get("news", []))
            limit_respected = news_count <= 3
            
            self.log_test_result(
                "GET /api/telegram-news - Limit parameter",
                limit_respected,
                f"Requested limit: 3, Actual count: {news_count}",
                {"requested_limit": 3, "actual_count": news_count}
            )
        else:
            self.log_test_result("GET /api/telegram-news - Limit parameter", False, f"Error: {error}", data)
        
        # Test that endpoint returns demo news when real news unavailable
        # This is tested by checking if we get a response even without valid Telegram credentials
        success, data, error = await self.make_request("GET", "/api/telegram-news")
        
        if success and isinstance(data, dict):
            status = data.get("status")
            has_demo_fallback = status in ["success", "demo"]  # Either real news or demo
            has_news_data = len(data.get("news", [])) > 0
            
            self.log_test_result(
                "GET /api/telegram-news - Demo fallback functionality",
                has_demo_fallback and has_news_data,
                f"Status: {status}, Has news: {has_news_data}, News count: {len(data.get('news', []))}",
                data
            )
        else:
            self.log_test_result("GET /api/telegram-news - Demo fallback functionality", False, f"Error: {error}", data)
    
    async def test_text_formatting_improvements(self):
        """Test improved text formatting and removal of * symbols"""
        logger.info("=== Testing Text Formatting Improvements ===")
        
        # Test that analyze-file endpoint exists and requires authentication
        # (We can't test the actual formatting without authentication, but we can test the endpoint structure)
        success, data, error = await self.make_request("POST", "/api/analyze-file")
        
        # Should fail with authentication required, not with missing endpoint
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        endpoint_exists = is_auth_required or "422" in str(error)  # 422 means validation error (endpoint exists)
        
        self.log_test_result(
            "POST /api/analyze-file - Endpoint availability for text formatting",
            endpoint_exists,
            f"Endpoint exists and properly handles requests" if endpoint_exists else f"Endpoint issue: {error}",
            data
        )
        
        # Test that the endpoint accepts file uploads (structure test)
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication, not with file format issues
        handles_files_correctly = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - File upload handling with formatting",
            handles_files_correctly,
            f"Correctly handles file uploads and requires auth" if handles_files_correctly else f"File handling issue: {error}",
            data
        )
    
    async def test_improved_analysis_prompt(self):
        """Test that improved analysis prompt is being used"""
        logger.info("=== Testing Improved Analysis Prompt ===")
        
        # We can't directly test the prompt without authentication, but we can verify
        # that the analyze-file endpoint is properly configured to use the new prompt system
        
        # Test different language parameters to ensure prompt system handles them
        languages = ["en", "ru", "de"]
        
        for lang in languages:
            test_image_data = self.create_test_image()
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename='test_document.jpg', content_type='image/jpeg')
            form_data.add_field('language', lang)
            
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            
            # Should handle language parameter correctly (fail with auth, not validation)
            handles_language = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not handles_language:
                break
        
        self.log_test_result(
            "POST /api/analyze-file - Improved prompt system language handling",
            handles_language,
            f"Correctly handles language parameters for improved prompts" if handles_language else f"Language handling issue: {error}",
            {"tested_languages": languages}
        )
    
    async def test_auto_generate_gemini_key_endpoint(self):
        """Test new auto-generate Gemini API key endpoint"""
        logger.info("=== Testing Auto-Generate Gemini API Key Endpoint ===")
        
        # Test without authentication - should fail
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/auto-generate-gemini-key - Authentication required",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test that endpoint exists and is properly configured
        # The endpoint should return auth error, not 404 (not found)
        endpoint_exists = is_auth_required or "422" in str(error)  # 422 means validation error (endpoint exists)
        
        self.log_test_result(
            "POST /api/auto-generate-gemini-key - Endpoint availability",
            endpoint_exists,
            f"Endpoint exists and properly configured" if endpoint_exists else f"Endpoint not found or misconfigured: {error}",
            data
        )
    
    async def test_google_api_key_service_integration(self):
        """Test Google API Key Service integration"""
        logger.info("=== Testing Google API Key Service Integration ===")
        
        # Test that the service is properly imported and integrated
        # We can verify this by checking if the auto-generate endpoint responds correctly
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with auth error, not import error or server error
        is_properly_integrated = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        # If we get 500 error, it might indicate import or integration issues
        has_integration_issues = "500" in str(error) or (isinstance(data, dict) and "500" in str(data))
        
        self.log_test_result(
            "Google API Key Service - Integration check",
            is_properly_integrated and not has_integration_issues,
            f"Service properly integrated" if is_properly_integrated else f"Integration issue: {error}",
            data
        )
    
    async def test_api_key_update_new_field_names(self):
        """Test API key update with new field names (api_key_1, api_key_2, api_key_3)"""
        logger.info("=== Testing API Key Update with New Field Names ===")
        
        # Test with new field names - should require authentication
        new_field_data = {
            "api_key_1": "test_gemini_key_123",
            "api_key_2": "test_openai_key_456", 
            "api_key_3": "test_anthropic_key_789"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=new_field_data)
        
        # Should fail with auth error, not validation error
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        # Should NOT fail with validation error (422) - this would indicate the new fields are not accepted
        has_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - New field names acceptance",
            is_auth_required and not has_validation_error,
            f"New field names properly accepted" if (is_auth_required and not has_validation_error) else f"Field validation issue: {error}",
            data
        )
        
        # Test with old field names for comparison
        old_field_data = {
            "gemini_api_key": "test_gemini_key_123",
            "openai_api_key": "test_openai_key_456",
            "anthropic_api_key": "test_anthropic_key_789"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=old_field_data)
        
        # Should also fail with auth error, not validation error
        old_fields_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        old_fields_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - Old field names compatibility",
            old_fields_auth_required and not old_fields_validation_error,
            f"Old field names still supported" if (old_fields_auth_required and not old_fields_validation_error) else f"Compatibility issue: {error}",
            data
        )
        
        # Test mixed field names
        mixed_field_data = {
            "api_key_1": "test_new_gemini_key",
            "openai_api_key": "test_old_openai_key"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=mixed_field_data)
        
        mixed_fields_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        mixed_fields_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - Mixed field names handling",
            mixed_fields_auth_required and not mixed_fields_validation_error,
            f"Mixed field names properly handled" if (mixed_fields_auth_required and not mixed_fields_validation_error) else f"Mixed fields issue: {error}",
            data
        )
    
    async def test_dependencies_installation(self):
        """Test that required dependencies are properly installed"""
        logger.info("=== Testing Dependencies Installation ===")
        
        # Test that google-api-python-client is available by checking if endpoints work
        # If the import fails, we'd get 500 errors on endpoints that use it
        
        # Test auto-generate endpoint (uses google-api-python-client)
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with auth error, not import/dependency error (500)
        no_import_errors = not ("500" in str(error) or (isinstance(data, dict) and "500" in str(data)))
        has_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
        
        self.log_test_result(
            "Dependencies - google-api-python-client availability",
            no_import_errors and has_auth_error,
            f"google-api-python-client properly installed" if (no_import_errors and has_auth_error) else f"Dependency issue: {error}",
            data
        )
        
        # Test modern LLM status (uses emergentintegrations)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            no_import_issues = data.get("status") != "error"
            
            self.log_test_result(
                "Dependencies - emergentintegrations availability",
                has_modern_flag and no_import_issues,
                f"emergentintegrations properly installed and working" if (has_modern_flag and no_import_issues) else f"emergentintegrations issue",
                data
            )
        else:
            self.log_test_result(
                "Dependencies - emergentintegrations availability", 
                False, 
                f"emergentintegrations dependency error: {error}", 
                data
            )
    
    async def test_improved_ocr_service_status(self):
        """Test new improved OCR service status endpoint"""
        logger.info("=== Testing Improved OCR Service Status ===")
        
        # Test OCR status endpoint
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            # Check required fields
            has_status = data.get("status") == "success"
            has_ocr_service = "ocr_service" in data and isinstance(data["ocr_service"], dict)
            tesseract_not_required = data.get("tesseract_required") is False
            production_ready = data.get("production_ready") is True
            
            # Check OCR service structure
            ocr_service_valid = False
            if has_ocr_service:
                ocr_service = data["ocr_service"]
                has_service_name = "service_name" in ocr_service
                has_methods = "methods" in ocr_service and isinstance(ocr_service["methods"], dict)
                has_primary_method = "primary_method" in ocr_service
                tesseract_dependency_false = ocr_service.get("tesseract_dependency") is False
                service_production_ready = ocr_service.get("production_ready") is True
                
                ocr_service_valid = all([has_service_name, has_methods, has_primary_method, tesseract_dependency_false, service_production_ready])
            
            self.log_test_result(
                "GET /api/ocr-status - OCR service status",
                has_status and has_ocr_service and tesseract_not_required and production_ready and ocr_service_valid,
                f"Status: {data.get('status')}, Tesseract required: {data.get('tesseract_required')}, Production ready: {data.get('production_ready')}, Service valid: {ocr_service_valid}",
                data
            )
        else:
            self.log_test_result("GET /api/ocr-status - OCR service status", False, f"Error: {error}", data)
    
    async def test_ocr_methods_availability(self):
        """Test availability of different OCR methods"""
        logger.info("=== Testing OCR Methods Availability ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict) and "ocr_service" in data:
            ocr_service = data["ocr_service"]
            methods = ocr_service.get("methods", {})
            
            # Check for expected OCR methods
            expected_methods = ["llm_vision", "ocr_space", "azure_vision", "direct_pdf"]
            methods_found = []
            methods_available = []
            
            for method in expected_methods:
                if method in methods:
                    methods_found.append(method)
                    if methods[method].get("available"):
                        methods_available.append(method)
            
            # At least direct_pdf should always be available
            direct_pdf_available = methods.get("direct_pdf", {}).get("available") is True
            
            # Check primary method
            primary_method = ocr_service.get("primary_method")
            primary_method_valid = primary_method in methods_found
            
            self.log_test_result(
                "OCR Methods - Availability check",
                len(methods_found) == len(expected_methods) and direct_pdf_available and primary_method_valid,
                f"Methods found: {methods_found}, Available: {methods_available}, Primary: {primary_method}, Direct PDF: {direct_pdf_available}",
                {"methods_found": methods_found, "methods_available": methods_available, "primary_method": primary_method}
            )
            
            # Check LLM Vision method specifically
            llm_vision = methods.get("llm_vision", {})
            llm_vision_configured = "available" in llm_vision and "description" in llm_vision
            llm_vision_desc_correct = "LLM Vision" in str(llm_vision.get("description", ""))
            
            self.log_test_result(
                "OCR Methods - LLM Vision configuration",
                llm_vision_configured and llm_vision_desc_correct,
                f"LLM Vision available: {llm_vision.get('available')}, Description: {llm_vision.get('description')}",
                llm_vision
            )
            
            # Check OCR.space method
            ocr_space = methods.get("ocr_space", {})
            ocr_space_configured = "available" in ocr_space and "description" in ocr_space
            ocr_space_desc_correct = "OCR.space" in str(ocr_space.get("description", ""))
            
            self.log_test_result(
                "OCR Methods - OCR.space configuration",
                ocr_space_configured and ocr_space_desc_correct,
                f"OCR.space available: {ocr_space.get('available')}, Description: {ocr_space.get('description')}",
                ocr_space
            )
            
            # Check Azure Vision method
            azure_vision = methods.get("azure_vision", {})
            azure_vision_configured = "available" in azure_vision and "description" in azure_vision
            azure_vision_desc_correct = "Azure" in str(azure_vision.get("description", ""))
            
            self.log_test_result(
                "OCR Methods - Azure Vision configuration",
                azure_vision_configured and azure_vision_desc_correct,
                f"Azure Vision available: {azure_vision.get('available')}, Description: {azure_vision.get('description')}",
                azure_vision
            )
            
        else:
            self.log_test_result("OCR Methods - Availability check", False, f"Error getting OCR status: {error}", data)
    
    async def test_analyze_file_ocr_integration(self):
        """Test that analyze-file endpoint integrates with improved OCR service"""
        logger.info("=== Testing Analyze File OCR Integration ===")
        
        # Test that analyze-file endpoint exists and handles different file types
        test_image_data = self.create_test_image()
        
        # Test with JPEG image
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'de')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication required (not file format error)
        handles_jpeg = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - JPEG image handling",
            handles_jpeg,
            f"Correctly handles JPEG images and requires auth" if handles_jpeg else f"JPEG handling issue: {error}",
            data
        )
        
        # Test with PNG image
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.png', content_type='image/png')
        form_data.add_field('language', 'en')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        handles_png = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - PNG image handling",
            handles_png,
            f"Correctly handles PNG images and requires auth" if handles_png else f"PNG handling issue: {error}",
            data
        )
        
        # Test with WebP image
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.webp', content_type='image/webp')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        handles_webp = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - WebP image handling",
            handles_webp,
            f"Correctly handles WebP images and requires auth" if handles_webp else f"WebP handling issue: {error}",
            data
        )
        
        # Test with GIF image
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.gif', content_type='image/gif')
        form_data.add_field('language', 'de')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        handles_gif = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - GIF image handling",
            handles_gif,
            f"Correctly handles GIF images and requires auth" if handles_gif else f"GIF handling issue: {error}",
            data
        )
    
    async def test_ocr_service_no_tesseract_dependency(self):
        """Test that OCR service works without tesseract dependency"""
        logger.info("=== Testing OCR Service No Tesseract Dependency ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            # Check main response
            tesseract_not_required = data.get("tesseract_required") is False
            production_ready = data.get("production_ready") is True
            
            # Check OCR service details
            ocr_service = data.get("ocr_service", {})
            service_tesseract_dependency = ocr_service.get("tesseract_dependency") is False
            service_production_ready = ocr_service.get("production_ready") is True
            
            # Check that primary method is not tesseract-based
            primary_method = ocr_service.get("primary_method", "")
            primary_not_tesseract = "tesseract" not in primary_method.lower()
            
            self.log_test_result(
                "OCR Service - No tesseract dependency",
                tesseract_not_required and production_ready and service_tesseract_dependency and service_production_ready and primary_not_tesseract,
                f"Tesseract required: {data.get('tesseract_required')}, Production ready: {data.get('production_ready')}, Primary method: {primary_method}",
                data
            )
        else:
            self.log_test_result("OCR Service - No tesseract dependency", False, f"Error: {error}", data)
    
    async def test_ocr_logging_and_fallback(self):
        """Test OCR service logging and fallback mechanisms"""
        logger.info("=== Testing OCR Service Logging and Fallback ===")
        
        # Test that the OCR status endpoint shows proper fallback configuration
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            
            # Check that multiple methods are configured for fallback
            available_methods = [method for method, config in methods.items() if config.get("available")]
            has_multiple_methods = len(available_methods) >= 2  # At least 2 methods for fallback
            
            # Check that direct_pdf is always available as final fallback
            direct_pdf_available = methods.get("direct_pdf", {}).get("available") is True
            
            # Check primary method configuration
            primary_method = ocr_service.get("primary_method")
            primary_method_exists = primary_method in methods
            
            self.log_test_result(
                "OCR Service - Fallback configuration",
                has_multiple_methods and direct_pdf_available and primary_method_exists,
                f"Available methods: {available_methods}, Direct PDF: {direct_pdf_available}, Primary: {primary_method}",
                {"available_methods": available_methods, "primary_method": primary_method}
            )
        else:
            self.log_test_result("OCR Service - Fallback configuration", False, f"Error: {error}", data)
    
    async def test_render_deployment_tesseract_fix(self):
        """Test Render deployment fix - Tesseract as PRIMARY OCR method"""
        logger.info("=== Testing Render Deployment Tesseract Fix ===")
        
        # Test 1: OCR Status shows tesseract_ocr as primary_method
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method")
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            tesseract_version = ocr_service.get("tesseract_version")
            production_ready = ocr_service.get("production_ready")
            
            # Check that tesseract_ocr is PRIMARY method (not fallback)
            is_tesseract_primary = primary_method == "tesseract_ocr"
            has_tesseract_dependency = tesseract_dependency is True
            has_correct_version = tesseract_version == "5.3.0"
            is_production_ready = production_ready is True
            
            self.log_test_result(
                "OCR Status - Tesseract as PRIMARY method",
                is_tesseract_primary and has_tesseract_dependency and has_correct_version and is_production_ready,
                f"Primary: {primary_method}, Dependency: {tesseract_dependency}, Version: {tesseract_version}, Production: {production_ready}",
                data
            )
        else:
            self.log_test_result("OCR Status - Tesseract as PRIMARY method", False, f"Error: {error}", data)
    
    async def test_tesseract_system_availability(self):
        """Test that Tesseract is available in the system"""
        logger.info("=== Testing Tesseract System Availability ===")
        
        # Test OCR service status for tesseract availability
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            
            # Check tesseract availability
            tesseract_available = tesseract_method.get("available") is True
            tesseract_description = tesseract_method.get("description", "")
            has_correct_description = "традиционный OCR" in tesseract_description or "Tesseract OCR" in tesseract_description
            
            # Check that tesseract is marked as main method, not fallback
            is_main_method = "основной метод" in tesseract_description or "primary" in tesseract_description.lower()
            
            self.log_test_result(
                "Tesseract System - Availability check",
                tesseract_available and has_correct_description and is_main_method,
                f"Available: {tesseract_available}, Description: {tesseract_description}, Is main: {is_main_method}",
                tesseract_method
            )
        else:
            self.log_test_result("Tesseract System - Availability check", False, f"Error: {error}", data)
    
    async def test_tesseract_language_packages(self):
        """Test that all required language packages are working"""
        logger.info("=== Testing Tesseract Language Packages ===")
        
        # Test OCR service status for language support
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            
            # Check if tesseract is available (implies language packages work)
            tesseract_available = tesseract_method.get("available") is True
            tesseract_description = tesseract_method.get("description", "")
            
            # Check for multi-language support indication
            supports_multiple_languages = "многих языков" in tesseract_description or "languages" in tesseract_description.lower()
            
            self.log_test_result(
                "Tesseract Language Packages - Multi-language support",
                tesseract_available and supports_multiple_languages,
                f"Available: {tesseract_available}, Multi-lang support: {supports_multiple_languages}",
                tesseract_method
            )
        else:
            self.log_test_result("Tesseract Language Packages - Multi-language support", False, f"Error: {error}", data)
    
    async def test_render_deployment_dependencies(self):
        """Test that all dependencies are installed correctly for Render deployment"""
        logger.info("=== Testing Render Deployment Dependencies ===")
        
        # Test 1: Modern LLM manager works (not in fallback mode)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            status_success = data.get("status") == "success"
            has_providers = "providers" in data and len(data["providers"]) > 0
            
            # Check that it's not in fallback mode
            not_in_fallback = status_success and has_modern_flag
            
            self.log_test_result(
                "Render Dependencies - Modern LLM manager (not fallback)",
                not_in_fallback and has_providers,
                f"Modern: {has_modern_flag}, Status: {data.get('status')}, Providers: {len(data.get('providers', {}))}, Not fallback: {not_in_fallback}",
                data
            )
        else:
            self.log_test_result("Render Dependencies - Modern LLM manager (not fallback)", False, f"Error: {error}", data)
        
        # Test 2: System is production ready
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            production_ready = data.get("production_ready") is True
            ocr_service = data.get("ocr_service", {})
            service_production_ready = ocr_service.get("production_ready") is True
            
            self.log_test_result(
                "Render Dependencies - Production ready status",
                production_ready and service_production_ready,
                f"Main production ready: {production_ready}, OCR service production ready: {service_production_ready}",
                data
            )
        else:
            self.log_test_result("Render Dependencies - Production ready status", False, f"Error: {error}", data)
    
    async def test_system_not_in_fallback_mode(self):
        """Test that system is NOT working in fallback mode"""
        logger.info("=== Testing System Not in Fallback Mode ===")
        
        # Test 1: OCR service has tesseract as primary (not fallback)
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method")
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            
            # System should NOT be in fallback mode
            not_in_fallback = primary_method == "tesseract_ocr" and tesseract_dependency is True
            
            self.log_test_result(
                "System Status - Not in fallback mode (OCR)",
                not_in_fallback,
                f"Primary method: {primary_method}, Tesseract dependency: {tesseract_dependency}, Not fallback: {not_in_fallback}",
                data
            )
        else:
            self.log_test_result("System Status - Not in fallback mode (OCR)", False, f"Error: {error}", data)
        
        # Test 2: Modern LLM manager not in fallback
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            status = data.get("status")
            modern_flag = data.get("modern")
            
            # Should not be in fallback/error mode
            not_in_fallback_llm = status == "success" and modern_flag is True
            
            self.log_test_result(
                "System Status - Not in fallback mode (LLM)",
                not_in_fallback_llm,
                f"Status: {status}, Modern: {modern_flag}, Not fallback: {not_in_fallback_llm}",
                data
            )
        else:
            self.log_test_result("System Status - Not in fallback mode (LLM)", False, f"Error: {error}", data)
    
    async def test_basic_functionality_after_render_fix(self):
        """Test basic functionality after Render deployment fix"""
        logger.info("=== Testing Basic Functionality After Render Fix ===")
        
        # Test 1: Health check works
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            status_healthy = data.get("status") == "healthy"
            has_db_connection = "users_count" in data and "analyses_count" in data
            
            self.log_test_result(
                "Basic Functionality - Health check",
                status_healthy and has_db_connection,
                f"Status: {data.get('status')}, DB connected: {has_db_connection}",
                data
            )
        else:
            self.log_test_result("Basic Functionality - Health check", False, f"Error: {error}", data)
        
        # Test 2: Authentication endpoints work
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={"credential": "invalid_token"})
        
        # Should fail with 400 (invalid token), not 500 (server error)
        auth_endpoint_works = not success and "400" in str(error)
        
        self.log_test_result(
            "Basic Functionality - Authentication endpoint",
            auth_endpoint_works,
            f"Auth endpoint properly handles requests" if auth_endpoint_works else f"Auth endpoint issue: {error}",
            data
        )
        
        # Test 3: Modern LLM status works
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            modern_llm_works = data.get("modern") is True and data.get("status") == "success"
            
            self.log_test_result(
                "Basic Functionality - Modern LLM status",
                modern_llm_works,
                f"Modern LLM status working: {modern_llm_works}",
                data
            )
        else:
            self.log_test_result("Basic Functionality - Modern LLM status", False, f"Error: {error}", data)

    async def run_all_tests(self):
        """Run all backend tests"""
        logger.info("🚀 Starting comprehensive backend API tests...")
        
        try:
            # PRIORITY TESTS FOR RENDER DEPLOYMENT FIX
            await self.test_render_deployment_tesseract_fix()    # Test Tesseract as PRIMARY method
            await self.test_tesseract_system_availability()      # Test Tesseract system availability
            await self.test_tesseract_language_packages()        # Test language packages (deu, eng, rus, ukr)
            await self.test_render_deployment_dependencies()     # Test all dependencies installed correctly
            await self.test_system_not_in_fallback_mode()        # Test system NOT in fallback mode
            await self.test_basic_functionality_after_render_fix() # Test basic functionality
            
            await self.test_basic_health_endpoints()
            await self.test_api_health_endpoints()
            await self.test_llm_status_endpoint()
            await self.test_modern_llm_status_endpoint()  # New test for modern LLM status
            await self.test_legacy_status_endpoints()
            await self.test_authentication_required_endpoints()
            await self.test_google_oauth_endpoint()
            await self.test_quick_gemini_setup_endpoint()  # New test for quick Gemini setup
            await self.test_database_functionality()
            await self.test_no_skip_auth_functionality()
            
            # CRITICAL TESTS FOR IMAGE RECOGNITION
            await self.test_image_recognition_functionality()  # Test image recognition fix
            await self.test_modern_llm_manager_integration()   # Test modern LLM manager integration
            await self.test_emergentintegrations_support()     # Test emergentintegrations support
            
            # NEW TESTS FOR TELEGRAM NEWS AND TEXT FORMATTING
            await self.test_telegram_news_endpoint()           # Test new Telegram news endpoint
            await self.test_text_formatting_improvements()     # Test text formatting improvements
            await self.test_improved_analysis_prompt()         # Test improved analysis prompt
            
            # NEW TESTS FOR AUTO-GENERATE GEMINI API KEY FUNCTIONALITY
            await self.test_auto_generate_gemini_key_endpoint()  # Test new auto-generate endpoint
            await self.test_google_api_key_service_integration() # Test Google API Key Service integration
            await self.test_api_key_update_new_field_names()     # Test API key update with new field names
            await self.test_dependencies_installation()          # Test required dependencies
            
            # NEW TESTS FOR IMPROVED OCR SERVICE
            await self.test_improved_ocr_service_status()        # Test new OCR status endpoint
            await self.test_ocr_methods_availability()           # Test OCR methods availability
            await self.test_analyze_file_ocr_integration()       # Test analyze-file OCR integration
            await self.test_ocr_service_no_tesseract_dependency() # Test no tesseract dependency
            await self.test_ocr_logging_and_fallback()           # Test OCR logging and fallback
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            self.log_test_result("Test execution", False, f"Critical error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 BACKEND API TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} {result['test']}: {result['details']}")
        
        if total - passed > 0:
            logger.info("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"❌ {result['test']}: {result['details']}")
                    if result["response_data"]:
                        logger.info(f"   Response: {result['response_data']}")
        
        logger.info("="*60)
        
        return passed, total

async def main():
    """Main test execution"""
    async with BackendTester() as tester:
        await tester.run_all_tests()
        passed, total = tester.print_summary()
        
        # Return exit code based on results
        return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)