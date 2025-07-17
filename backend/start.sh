#!/bin/bash
# Улучшенный start.sh для Render.com - правильная диагностика и запуск

echo "🚀 Starting German AI Backend v13.0 - Render Production Mode..."

# Показываем рабочую директорию и PATH
echo "Working directory: $(pwd)"
echo "Current PATH: $PATH"

# Проверяем доступность tesseract
echo "Checking tesseract availability..."
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH: $(which tesseract)"
    tesseract --version | head -1
    
    # Проверяем языковые пакеты
    echo "Available languages:"
    tesseract --list-langs 2>/dev/null || echo "Could not list languages"
else
    echo "❌ tesseract not found in PATH"
    echo "⚠️ OCR functionality will be limited"
fi

# Проверяем emergentintegrations
echo "Checking emergentintegrations..."
if python -c "import emergentintegrations; print('emergentintegrations version:', emergentintegrations.__version__ if hasattr(emergentintegrations, '__version__') else 'unknown')" 2>/dev/null; then
    echo "✅ emergentintegrations available"
else
    echo "❌ emergentintegrations not available"
    echo "⚠️ Running in fallback mode without emergentintegrations"
fi

# Проверяем основные зависимости
echo "Checking Python dependencies..."
python -c "import pytesseract; print('pytesseract OK')" 2>/dev/null || echo "❌ pytesseract not available"
python -c "import cv2; print('opencv-python OK')" 2>/dev/null || echo "❌ opencv-python not available"
python -c "import PIL; print('Pillow OK')" 2>/dev/null || echo "❌ Pillow not available"
python -c "import httpcore; print('httpcore OK')" 2>/dev/null || echo "❌ httpcore not available"

# Проверяем доступность основных модулей приложения
echo "Checking app modules..."
python -c "from modern_llm_manager import modern_llm_manager; print('modern_llm_manager OK')" 2>/dev/null || echo "❌ modern_llm_manager not available"

echo "🔧 System diagnostics complete"

# Создаем директорию для базы данных в правильном месте
mkdir -p /opt/render/project/src/backend/data 2>/dev/null || echo "Using default database path"

# Проверяем что сервер файл существует
if [ -f "server.py" ]; then
    echo "✅ server.py found"
else
    echo "❌ server.py not found in $(pwd)"
    echo "Files in current directory:"
    ls -la
    exit 1
fi

# Устанавливаем переменные окружения для Render
export TESSERACT_AVAILABLE=true
export TESSERACT_VERSION=5.3.0
export SQLITE_DB_PATH=/opt/render/project/src/backend/data/german_ai.db

# Запускаем сервер с правильным портом для Render
echo "✅ Starting uvicorn server on port ${PORT:-8001} in production mode..."
exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1