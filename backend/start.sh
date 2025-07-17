#!/bin/bash
# ИСПРАВЛЕНО: Улучшенный start.sh для Render.com v11.0 с исправлением tesseract PATH

echo "🚀 Starting German AI Backend v11.0 - TESSERACT PATH FIX..."

# Показываем текущий PATH
echo "Current PATH: $PATH"

# Проверяем все возможные местоположения tesseract
echo "Searching for tesseract..."
find /usr -name "tesseract" -type f 2>/dev/null | head -5
which tesseract 2>/dev/null || echo "which tesseract: not found"
ls -la /usr/bin/tesseract 2>/dev/null || echo "/usr/bin/tesseract: not found"
ls -la /usr/local/bin/tesseract 2>/dev/null || echo "/usr/local/bin/tesseract: not found"

# Пробуем установить tesseract если не найден
if ! command -v tesseract &> /dev/null; then
    echo "❌ tesseract not found, trying to install..."
    
    if command -v apt-get &> /dev/null; then
        echo "Installing tesseract with apt-get..."
        apt-get update && apt-get install -y \
            tesseract-ocr \
            tesseract-ocr-deu \
            tesseract-ocr-rus \
            tesseract-ocr-eng \
            tesseract-ocr-ukr \
        && echo "✅ tesseract installed" \
        || echo "❌ failed to install tesseract"
    else
        echo "❌ apt-get not available, cannot install tesseract"
    fi
fi

# Проверяем tesseract еще раз
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH"
    tesseract --version | head -1
    
    # Проверяем языковые пакеты
    echo "Checking language packs..."
    tesseract --list-langs 2>/dev/null || echo "Could not list languages"
else
    echo "❌ tesseract still not found in PATH"
    echo "Available commands in /usr/bin:"
    ls /usr/bin/ | grep -E "(tesseract|ocr)" || echo "No OCR tools found"
    echo "⚠️ OCR functionality will be limited"
fi

# Проверяем emergentintegrations
echo "Testing emergentintegrations..."
if python -c "import emergentintegrations; print('emergentintegrations OK')" 2>/dev/null; then
    echo "✅ emergentintegrations available"
else
    echo "❌ emergentintegrations not available"
    echo "⚠️ Running in fallback mode without emergentintegrations"
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

# Создаем директорию для базы данных
mkdir -p /app/data 2>/dev/null || echo "Could not create /app/data directory"

# Проверяем что сервер файл существует
if [ -f "server.py" ]; then
    echo "✅ server.py found"
else
    echo "❌ server.py not found in $(pwd)"
    echo "Files in current directory:"
    ls -la
    exit 1
fi

echo "✅ Starting uvicorn server..."
exec uvicorn server:app --host 0.0.0.0 --port 8001 --reload