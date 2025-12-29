# 🏆 Habit Tracker API - Трекер полезных привычек

REST API для отслеживания полезных привычек с автоматическими Telegram уведомлениями.

## 🎯 Функционал

### Основные возможности:
- 📝 **Управление привычками** - создание, чтение, обновление, удаление
- 🔐 **Безопасная аутентификация** - JWT токены
- ⚖️ **Валидация бизнес-правил** - все требования задания
- 🤖 **Telegram уведомления** - автоматические напоминания
- ⏰ **Планировщик задач** - Celery для периодических проверок
- 🔒 **Права доступа** - только владельцы могут изменять свои привычки
- 📄 **Пагинация** - вывод по 5 привычек на страницу
- 📚 **Документация** - Swagger UI

### Бизнес-правила (валидация):
1. ⏱ **Время выполнения** - не более 120 секунд
2. 📅 **Периодичность** - не более 7 дней
3. 😊 **Приятные привычки** - не могут иметь вознаграждения
4. 🔗 **Связанные привычки** - только приятные привычки
5. 🎁 **Вознаграждение vs Связь** - нельзя выбрать одновременно

## 🚀 Быстрый старт

### 1. Установка
```
git clone <repository-url>
cd habit_tracker
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Настройка

#### Создайте .env файл:
```
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
TELEGRAM_BOT_TOKEN=ваш-токен-бота
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 3. Запуск

```# Миграции
python manage.py migrate
python manage.py createsuperuser

# Сервер Django
python manage.py runserver

# Celery worker (Windows)
celery -A config worker --pool=solo
```

## 📡 API Endpoints

### 🔐 Аутентификация

- POST /api/register/ - Регистрация пользователя
- POST /api/token/ - Получение JWT токена
- POST /api/token/refresh/ - Обновление токена
- GET /api/profile/ - Профиль пользователя

### 📝 Привычки

- GET /api/habits/ - Мои привычки (пагинация)
- POST /api/habits/ - Создание привычки
- GET /api/habits/{id}/ - Детали привычки
- PUT/PATCH /api/habits/{id}/ - Обновление привычки
- DELETE /api/habits/{id}/ - Удаление привычки
- GET /api/public-habits/ - Публичные привычки

### 🤖 Telegram

- POST /api/telegram/connect/ - Подключение Telegram

## 🧪 Тестирование

#### Проект имеет 100% покрытие тестами:
```
# Установите зависимости
pip install -r requirements.txt

# Запуск всех тестов
pytest 

# Запуск с покрытием
pytest --cov=habits --cov=users --cov-report=html
```

## 🛠 Технологии
- Backend: Django 5.2 + Django REST Framework
- Аутентификация: JWT (Simple JWT)
- Очереди задач: Celery + Redis
- Уведомления: Telegram Bot API
- Тестирование: pytest + coverage
- Документация: drf-spectacular (Swagger)
- База данных: SQLite/PostgreSQL

## 📄 Документация

### Для подключения Telegram:

1. Создайте бота через @BotFather
2. Добавьте токен в .env
3. Найдите chat_id через @userinfobot
4. Отправьте POST на /api/telegram/connect/ с chat_id


### 📄 Лицензия
MIT License