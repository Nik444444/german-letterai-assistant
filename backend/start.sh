#!/bin/bash
# ИСПРАВЛЕНО: Улучшенный start.sh для Render.com v10.0 с лучшей обработкой ошибок
# Фокус на запуске сервера с проверкой зависимостей

echo "🚀 Starting German AI Backend v10.0 - PRODUCTION FIX..."

# Проверяем tesseract
echo "Testing tesseract..."
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH"
    tesseract --version | head -1
else
    echo "❌ tesseract not found in PATH"
    echo "PATH: $PATH"
    echo "⚠️  OCR functionality will be limited"
fi

# Проверяем emergentintegrations
echo "Testing emergentintegrations..."
if python -c "import emergentintegrations; print('emergentintegrations OK')" 2>/dev/null; then
    echo "✅ emergentintegrations available"
else
    echo "❌ emergentintegrations not available"
    echo "Trying to install emergentintegrations..."
    pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ --trusted-host d33sy5i8bnduwe.cloudfront.net 2>/dev/null || echo "❌ Failed to install emergentintegrations"
    
    if python -c "import emergentintegrations; print('emergentintegrations OK')" 2>/dev/null; then
        echo "✅ emergentintegrations installed successfully"
    else
        echo "❌ emergentintegrations still not available"
        echo "⚠️  Running in fallback mode without emergentintegrations"
    fi
fi

# Проверяем основные зависимости
echo "Testing Python dependencies..."
python -c "import pytesseract; print('pytesseract OK')" 2>/dev/null || echo "❌ pytesseract not available"
python -c "import cv2; print('opencv-python OK')" 2>/dev/null || echo "❌ opencv-python not available"
python -c "import PIL; print('Pillow OK')" 2>/dev/null || echo "❌ Pillow not available"

# Проверяем доступность основных модулей приложения
echo "Testing app modules..."
python -c "from modern_llm_manager import modern_llm_manager; print('modern_llm_manager OK')" 2>/dev/null || echo "❌ modern_llm_manager not available"
python -c "from database import db; print('database OK')" 2>/dev/null || echo "❌ database not available"

echo "🔧 System diagnostics complete"

# Проверяем что сервер файл существует
if [ -f "server.py" ]; then
    echo "✅ server.py found"
else
    echo "❌ server.py not found in $(pwd)"
    ls -la
    exit 1
fi

echo "✅ Starting uvicorn server..."
exec uvicorn server:app --host 0.0.0.0 --port 8001 --reload