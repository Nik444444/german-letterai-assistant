#!/bin/bash
# ИСПРАВЛЕНО: Упрощенный start.sh для Render.com v9.0
# Фокус на запуске сервера, так как зависимости устанавливаются в buildCommand

echo "🚀 Starting German AI Backend v9.0 - PRODUCTION FIX..."

# Проверяем tesseract
echo "Testing tesseract..."
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH"
    tesseract --version
else
    echo "❌ tesseract not found in PATH"
    echo "PATH: $PATH"
fi

# Проверяем emergentintegrations
echo "Testing emergentintegrations..."
if python -c "import emergentintegrations; print('emergentintegrations OK')" 2>/dev/null; then
    echo "✅ emergentintegrations available"
else
    echo "❌ emergentintegrations not available"
fi

# Проверяем основные зависимости
echo "Testing Python dependencies..."
python -c "import pytesseract; print('pytesseract OK')" || echo "❌ pytesseract not available"
python -c "import cv2; print('opencv-python OK')" || echo "❌ opencv-python not available"
python -c "import PIL; print('Pillow OK')" || echo "❌ Pillow not available"

echo "🔧 System diagnostics complete"

echo "✅ Starting uvicorn server..."
exec uvicorn server:app --host 0.0.0.0 --port 8001 --reload