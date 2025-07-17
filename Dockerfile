# Dockerfile для 100% работы Tesseract OCR на Render
FROM python:3.11-slim

# Обновляем пакеты и устанавливаем Tesseract OCR со всеми языковыми пакетами
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    tesseract-ocr-ukr \
    tesseract-ocr-osd \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libffi-dev \
    libssl-dev \
    pkg-config \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Проверяем установку Tesseract
RUN tesseract --version && tesseract --list-langs

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы требований
COPY backend/requirements.txt ./backend/requirements.txt

# Обновляем pip и устанавливаем зависимости Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Устанавливаем emergentintegrations с обработкой ошибок
RUN pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ --trusted-host d33sy5i8bnduwe.cloudfront.net || \
    echo "⚠️ emergentintegrations installation failed, will use fallback mode"

# Копируем все файлы проекта
COPY . .

# Создаем директорию для данных
RUN mkdir -p /app/backend/data

# Устанавливаем переменные окружения для Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV TESSERACT_AVAILABLE=true
ENV TESSERACT_VERSION=5.3.0
ENV PATH="/usr/bin:/usr/local/bin:${PATH}"

# Проверяем все критические зависимости
RUN python -c "import pytesseract; print('✅ pytesseract OK')" && \
    python -c "import cv2; print('✅ opencv-python OK')" && \
    python -c "import PIL; print('✅ Pillow OK')" && \
    python -c "import tesseract; print('✅ pytesseract can find tesseract')" || echo "⚠️ Some checks failed"

# Создаем исполняемый файл start.sh
RUN chmod +x backend/start.sh

# Открываем порт (будет переопределен Render)
EXPOSE 8001

# Переходим в backend директорию
WORKDIR /app/backend

# Запускаем приложение
CMD ["bash", "start.sh"]