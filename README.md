# Phil Backend - Negative Links CRM System

Backend API для внутренней CRM-системы учёта и обработки негативных ссылок.

## Технологический стек

- **Django 5.0** - Web framework
- **Django REST Framework** - REST API
- **PostgreSQL** - База данных
- **Redis** - Кэширование и Celery broker
- **Celery** - Фоновые задачи
- **Docker & Docker Compose** - Контейнеризация

## Функциональность

### API Эндпоинты

#### Авторизация (JWT)

Все эндпоинты `/api/links/` и `/api/stats/` требуют авторизации. Передавайте access-токен в заголовке: `Authorization: Bearer <access>`.

- `POST /api/auth/login/` — вход (username или email + password). Возвращает `access`, `refresh` и данные пользователя.
- `POST /api/auth/logout/` — выход (blacklist refresh-токена). Тело: `{"refresh": "<refresh_token>"}`.
- `POST /api/auth/refresh/` — обновление access-токена. Тело: `{"refresh": "<refresh_token>"}`.
- `GET /api/auth/me/` — текущий пользователь (требуется access-токен).

Срок жизни токенов: access — 1 час, refresh — 7 дней.

#### Менеджеры (CRUD)
- `GET /api/managers/` - Список менеджеров
- `POST /api/managers/` - Создать менеджера (name, email, is_active)
- `GET /api/managers/:id/` - Получить менеджера
- `PATCH /api/managers/:id/` - Обновить
- `DELETE /api/managers/:id/` - Мягкое удаление (is_active=false)

#### CRUD операции (ссылки)
- `GET /api/links/` - Список ссылок с фильтрацией (в ответе `manager` — объект {id, name, email, is_active})
- `GET /api/links/:id/` - Получить одну ссылку
- `POST /api/links/` - Создать ссылку (можно передать `manager_id` — UUID менеджера)
- `PATCH /api/links/:id/` - Обновить ссылку
- `DELETE /api/links/:id/` - Удалить ссылку

#### Bulk операции
- `POST /api/links/bulk-update-status/` - Массовое обновление статуса
- `POST /api/links/bulk-assign-manager/` - Массовое назначение менеджера (тело: `ids`, `manager_id` — UUID)

#### Статистика
- `GET /api/stats/dashboard/?period=1d|7d|30d` — общая статистика за период. По умолчанию `period=30d`. Учитываются ссылки с `detected_at` в выбранном интервале. Ответ: `period`, `total`, `active`, `removed`, `in_work`, `pending`, `cancelled`, `by_status` (в т.ч. `cancelled`), `platforms`, `by_priority`, `activity_chart` (по дням). Кэш в Redis 5 мин.
- `GET /api/stats/platform/:platform/?period=1d|7d|30d` — статистика по платформе за период (по умолчанию 30d). Ответ: `period`, `platform`, `total`, `active`, `removed`, `in_work`, `pending`, `cancelled`, `by_priority`. Кэш 5 мин.

#### Лог действий (Activity)
- `GET /api/activity/` — список записей лога (пагинация 100). Фильтры: `user`, `action`, `entity_type`, `date_from`, `date_to`. Требуется авторизация.
- `GET /api/activity/link/:link_id/` — лог по конкретной ссылке (пагинация 100).
- Действия логируются автоматически (создание/обновление/удаление ссылок, смена статуса, назначение менеджера). В лог не попадают чувствительные данные. Старые записи (>90 дней) удаляются задачей Celery `activity.tasks.cleanup_old_activity_logs` (по расписанию).

### Фильтры

API поддерживает следующие query параметры для фильтрации:
- `platform` - Платформа (facebook, twitter, youtube, reddit, other)
- `status` - Статус (active, removed, in_work, pending, cancelled)
- `priority` - Приоритет (low, medium, high)
- `manager_id` - UUID менеджера
- `dateFrom` - Дата начала (ISO 8601)
- `dateTo` - Дата окончания (ISO 8601)
- `search` - Поиск по URL

Пример: `/api/links/?platform=facebook&status=active&priority=high`

## Быстрый старт

### Предварительные требования

- Docker Desktop
- Docker Compose

### Установка и запуск

1. **Клонируйте репозиторий**
```bash
cd phil-backend
```

2. **Создайте файл .env**
```bash
cp .env.example .env
```

3. **Отредактируйте .env файл** (опционально)

Для локальной разработки значения по умолчанию в `.env.example` должны работать.

4. **Запустите Docker Compose**
```bash
docker-compose up --build
```

При первом запуске будут:
- Установлены все зависимости (включая djangorestframework-simplejwt)
- Созданы контейнеры
- Применены миграции БД (в т.ч. таблицы JWT token blacklist)
- Собраны статические файлы

5. **API будет доступен по адресу**
```
http://localhost:8000/api/
```

6. **Django Admin доступен по адресу**
```
http://localhost:8000/admin/
```

### Создание суперпользователя

```bash
docker-compose exec backend python manage.py createsuperuser
```

Следуйте инструкциям для создания администратора.

### Тестовый пользователь для проверки авторизации

**Если используешь Docker** (контейнер backend уже запущен):
```bash
docker compose exec backend python manage.py create_test_user
```
или сначала применить миграции (создадут пользователя автоматически):
```bash
docker compose exec backend python manage.py migrate
```

**Если видишь `command not found: docker`** — Docker не установлен или не запущен (нужен [Docker Desktop для Mac](https://docs.docker.com/desktop/install/mac-install/)). Тогда можно применить миграции и создать пользователя **локально** (в папке проекта, с установленными зависимостями и настроенной БД):
```bash
cd /Users/andrey/phil-backend/phil-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Укажи DATABASE_URL в .env или задай вручную
python3 manage.py migrate
python3 manage.py create_test_user
```

Будет создан пользователь: **логин** `phil_demo`, **пароль** `PhilDemo2026`  
(подходит для входа по username или по email `phil_demo@example.com`).

Промт для подключения авторизации на фронте: см. [FRONTEND_AUTH_PROMPT.md](FRONTEND_AUTH_PROMPT.md).

## Команды разработки

### Запуск сервисов
```bash
# Запустить все сервисы
docker-compose up

# Запустить в фоновом режиме
docker-compose up -d

# Пересобрать контейнеры
docker-compose up --build
```

### Остановка сервисов
```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v
```

### Работа с Django

```bash
# Выполнить команду в контейнере backend
docker-compose exec backend python manage.py <command>

# Примеры:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py makemigrations
```

### Логи

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f db
```

### Тестирование API

С помощью curl:

```bash
# 1. Авторизация (получить токены)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
# Ответ: {"access": "...", "refresh": "...", "user": {...}}
# Вместо "username" можно передать email.

# 2. Текущий пользователь
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"

# 3. Обновление access-токена
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'

# 4. Выход (blacklist refresh-токена)
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'

# 5. Защищённые эндпоинты — передавайте access в заголовке
export ACCESS_TOKEN="<your_access_token>"

# Список ссылок
curl http://localhost:8000/api/links/ -H "Authorization: Bearer $ACCESS_TOKEN"

# Создать ссылку
curl -X POST http://localhost:8000/api/links/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "url": "https://facebook.com/negative-post",
    "platform": "facebook",
    "type": "post",
    "priority": "high"
  }'

# Статистика
curl http://localhost:8000/api/stats/dashboard/ -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Структура проекта

```
phil-backend/
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile              # Docker image для backend
├── requirements.txt        # Python зависимости
├── manage.py              # Django CLI
├── .env.example           # Пример переменных окружения
├── .gitignore
├── phil/                  # Основной Django проект
│   ├── settings.py       # Настройки Django
│   ├── urls.py           # Основные URL routes
│   ├── wsgi.py           # WSGI конфигурация
│   ├── celery.py         # Celery конфигурация
│   └── __init__.py
├── accounts/              # Приложение авторизации (JWT)
│   ├── serializers.py    # Login, User serializers
│   ├── views.py          # Login, Logout, Refresh, Me
│   ├── middleware.py     # JWT token verification
│   └── urls.py           # /api/auth/ routes
├── links/                 # Приложение для управления ссылками
│   ├── models.py         # Модель NegativeLink
│   ├── serializers.py    # DRF Serializers
│   ├── views.py          # ViewSets и APIViews
│   ├── filters.py        # Фильтры для API
│   ├── admin.py          # Django Admin настройки
│   ├── tasks.py          # Celery tasks
│   └── urls.py           # URL routes
└── stats/                 # Приложение для статистики
    ├── views.py          # API views для статистики
    └── urls.py           # URL routes
```

## Модель данных

### NegativeLink

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Primary key (автогенерируемый) |
| url | TextField | URL негативного контента |
| platform | CharField | Платформа (facebook, twitter, youtube, reddit, other) |
| type | CharField | Тип контента (post, comment, video, article) |
| status | CharField | Статус (active, removed, in_work, pending, cancelled) |
| detected_at | DateTimeField | Дата обнаружения |
| removed_at | DateTimeField | Дата удаления (nullable) |
| priority | CharField | Приоритет (low, medium, high) |
| manager | CharField | Ответственный менеджер (nullable) |
| notes | TextField | Заметки (nullable) |
| created_at | DateTimeField | Дата создания записи |
| updated_at | DateTimeField | Дата обновления записи |

## Celery Tasks

### check_urls_availability

Периодическая задача для проверки доступности URL.

- **Расписание**: Каждые 24 часа (настраивается через `URL_CHECK_INTERVAL_HOURS`)
- **Включение/выключение**: `ENABLE_URL_CHECK_TASK` в .env
- **Функциональность**: 
  - Проверяет HTTP статус всех активных ссылок
  - Добавляет заметки о недоступных URL
  - Не изменяет статус автоматически (требуется ручная проверка)

### check_single_url

Задача для проверки одной конкретной ссылки.

```python
from links.tasks import check_single_url
result = check_single_url.delay(link_id)
```

## Настройки окружения

### Основные переменные

```env
DEBUG=True                                    # Debug режим
SECRET_KEY=your-secret-key                    # Django secret key
ALLOWED_HOSTS=localhost,127.0.0.1             # Разрешённые хосты
DATABASE_URL=postgresql://...                 # URL базы данных
REDIS_URL=redis://redis:6379/0                # Redis URL
CELERY_BROKER_URL=redis://redis:6379/0        # Celery broker
CORS_ALLOWED_ORIGINS=http://localhost:3000    # CORS origins
```

### Celery настройки

```env
ENABLE_URL_CHECK_TASK=False    # Включить автоматическую проверку URL
URL_CHECK_INTERVAL_HOURS=24    # Интервал проверки в часах
```

## Интеграция с Frontend

Frontend ожидает следующие настройки:

```env
# Frontend .env.local
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=http://localhost:8000
```

CORS настроен для фронтенда: в `CORS_ALLOWED_ORIGINS` укажите origin фронта (по умолчанию `http://localhost:3000`). Заголовок `Authorization` разрешён для JWT. Для запросов к защищённым эндпоинтам добавляйте заголовок: `Authorization: Bearer <access_token>`.

### Формат дат

Все даты возвращаются в ISO 8601 формате:
```
2026-02-17T12:34:56.789Z
```

### Формат ID

ID возвращаются как строки (UUID):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Production Deployment

### Важные изменения для production:

1. **Измените SECRET_KEY**
```env
SECRET_KEY=your-very-long-random-secret-key
```

2. **Отключите DEBUG**
```env
DEBUG=False
```

3. **Настройте ALLOWED_HOSTS**
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

4. **Настройте CORS**
```env
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

5. **Используйте управляемые сервисы БД и Redis**

6. **Настройте SSL/TLS**

7. **Используйте reverse proxy (nginx)**

8. **Настройте мониторинг и логирование**

## Логирование

Логи доступны:
- В консоли Docker: `docker-compose logs -f`
- В файле: `django.log` (внутри контейнера)

Уровень логирования настраивается через `DJANGO_LOG_LEVEL` в .env.

## Troubleshooting

### Backend не запускается

1. Проверьте логи: `docker-compose logs backend`
2. Убедитесь что порт 8000 свободен
3. Проверьте переменные окружения в .env

### База данных не подключается

1. Проверьте что контейнер db запущен: `docker-compose ps`
2. Проверьте логи БД: `docker-compose logs db`
3. Убедитесь что DATABASE_URL корректен

### Ошибка миграций

```bash
# Применить миграции вручную
docker-compose exec backend python manage.py migrate

# Создать новые миграции (если изменили модели)
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Celery задачи не выполняются

1. Проверьте что Redis запущен
2. Проверьте логи celery: `docker-compose logs celery`
3. Убедитесь что `ENABLE_URL_CHECK_TASK=True` если хотите включить проверку URL

## API Documentation

Для детальной документации API используйте Django REST Framework browsable API:

```
http://localhost:8000/api/
```

Или добавьте Swagger/OpenAPI документацию при необходимости.

## Лицензия

Internal use only.

## Контакты

Для вопросов и поддержки обращайтесь к команде разработки.
