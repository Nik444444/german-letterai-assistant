#!/bin/bash
# ИСПРАВЛЕНО: Упрощенный start.sh для Render.com - НЕ УСТАНАВЛИВАЕТ ПАКЕТЫ
# Используется только для диагностики и запуска приложения

echo "🚀 Starting German AI Backend v12.0 - Production Mode..."

# Показываем текущий PATH
echo "Current PATH: $PATH"

# Диагностика tesseract (только проверка, без установки)
echo "Checking tesseract availability..."
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH"
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
if python -c "import emergentintegrations; print('emergentintegrations OK')" 2>/dev/null; then
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

# Проверяем доступность основных модулей приложения
echo "Checking app modules..."
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

# Запускаем сервер без reload в production
echo "✅ Starting uvicorn server in production mode..."
exec uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1