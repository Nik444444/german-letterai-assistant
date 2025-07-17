# German Letter AI Assistant 🇩🇪

Современное веб-приложение для анализа немецких официальных писем с помощью искусственного интеллекта.

## 🚀 Возможности

- **Анализ документов**: PDF файлы и изображения
- **AI провайдеры**: Gemini, OpenAI, Anthropic
- **Многоязычность**: Русский, Английский, Немецкий
- **Безопасность**: Google OAuth авторизация
- **История**: Сохранение всех анализов
- **Современный дизайн**: Красивый и удобный интерфейс

## 🛠️ Технологии

**Backend:**
- FastAPI (Python)
- SQLite база данных
- Google OAuth 2.0
- AI/ML интеграции

**Frontend:**
- React 19
- Tailwind CSS
- Google OAuth
- React Router

## 📦 Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/your-username/german-letter-ai.git
   cd german-letter-ai
   ```

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Отредактируйте .env файл с вашими API ключами
   python server.py
   ```

3. **Frontend**
   ```bash
   cd frontend
   yarn install
   cp .env.example .env
   # Отредактируйте .env файл
   yarn start
   ```

### Развертывание на Render

📖 **Полная инструкция**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

Краткие шаги:
1. Получите API ключи (Google OAuth, AI провайдеры)
2. Создайте репозиторий на GitHub
3. Разверните на Render используя Docker
4. Настройте переменные окружения

## 🔑 Необходимые API ключи

1. **Google OAuth** (обязательно)
   - Получите в [Google Cloud Console](https://console.cloud.google.com)

2. **AI провайдеры** (хотя бы один)
   - **Gemini**: [ai.google.dev](https://ai.google.dev) (рекомендуется)
   - **OpenAI**: [platform.openai.com](https://platform.openai.com)
   - **Anthropic**: [console.anthropic.com](https://console.anthropic.com)

## 📁 Структура проекта

```
german-letter-ai/
├── backend/                 # FastAPI backend
│   ├── server.py           # Основной сервер
│   ├── database.py         # SQLite база данных
│   ├── llm_manager.py      # AI провайдеры
│   └── requirements.txt    # Python зависимости
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── context/        # React контексты
│   │   └── App.js         # Главное приложение
│   └── package.json       # Node.js зависимости
├── Dockerfile.backend     # Docker для backend
├── Dockerfile.frontend    # Docker для frontend
├── render.yaml           # Render конфигурация
└── DEPLOYMENT_GUIDE.md   # Инструкция по развертыванию
```

## 🔧 API Endpoints

- `GET /` - Информация о приложении
- `GET /health` - Проверка здоровья
- `POST /api/auth/google/verify` - Google OAuth
- `GET /api/profile` - Профиль пользователя
- `POST /api/api-keys` - Сохранение API ключей
- `POST /api/analyze-file` - Анализ файла
- `GET /api/analysis-history` - История анализов

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

Приветствуются любые предложения по улучшению!

1. Fork проекта
2. Создайте feature branch
3. Сделайте commit изменений
4. Push в branch
5. Создайте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории.
