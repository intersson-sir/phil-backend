# Промт: подключение авторизации к фронту (Phil Backend)

Подключи авторизацию к фронтенду для Phil Backend API.

## Контракт API

- **Base URL**: `NEXT_PUBLIC_API_URL` (например `http://localhost:8000`).
- Все запросы к `/api/links/` и `/api/stats/` должны отправляться с заголовком:
  `Authorization: Bearer <access_token>`.
- Токены приходят с бэкенда в ответе на логин; access — для заголовка, refresh — для обновления access без повторного логина.

## Эндпоинты авторизации

1. **Вход**  
   `POST {API_URL}/api/auth/login/`  
   Body (JSON): можно передать либо `"username": "логин или email"`, либо `"email": "email"`, либо оба — и обязательно `"password": "пароль"`. Примеры: `{ "username": "phil_demo", "password": "..." }` или `{ "email": "phil_demo@example.com", "password": "..." }`.  
   Ответ 200: `{ "access": "<access_token>", "refresh": "<refresh_token>", "user": { "id", "username", "email", "first_name", "last_name", "is_staff", "date_joined" } }`  
   Ошибки: 400 с полем `detail` или списком ошибок по полям.

2. **Выход**  
   `POST {API_URL}/api/auth/logout/`  
   Body (JSON): `{ "refresh": "<refresh_token>" }`  
   Ответ 200: `{ "detail": "Successfully logged out." }`  
   Refresh-токен после этого нельзя использовать (он в blacklist).

3. **Обновление access-токена**  
   `POST {API_URL}/api/auth/refresh/`  
   Body (JSON): `{ "refresh": "<refresh_token>" }`  
   Ответ 200: `{ "access": "<новый_access_token>" }`  
   Использовать когда access истёк (например 401), а refresh ещё действителен.

4. **Текущий пользователь**  
   `GET {API_URL}/api/auth/me/`  
   Заголовок: `Authorization: Bearer <access_token>`  
   Ответ 200: объект пользователя (те же поля, что в `user` при логине).

## Что сделать на фронте

1. **Хранение токенов и пользователя**  
   После успешного логина сохранять в безопасном месте (например httpOnly cookie или memory + refresh в httpOnly):  
   - `access` — для заголовка `Authorization: Bearer ...` во всех запросах к API.  
   - `refresh` — только для вызова `/api/auth/refresh/` и `/api/auth/logout/`.  
   Не логировать и не слать токены куда-либо кроме своего API.

2. **Заголовок для защищённых запросов**  
   Для каждого запроса к ` /api/links/` и `/api/stats/` добавлять заголовок:  
   `Authorization: Bearer <access_token>`.

3. **Обработка 401**  
   Если API вернул 401 на запрос с access-токеном:  
   - Вызвать `POST /api/auth/refresh/` с телом `{ "refresh": "<refresh_token>" }`.  
   - При 200 — сохранить новый `access` и повторить исходный запрос.  
   - При 401/400 на refresh — считать сессию недействительной: очистить токены и перенаправить на страницу входа.

4. **Выход**  
   По кнопке «Выйти»: отправить `POST /api/auth/logout/` с телом `{ "refresh": "<refresh_token>" }`, затем очистить токены и пользователя на фронте и перенаправить на логин.

5. **Восстановление сессии при загрузке приложения**  
   Если при старте приложения есть сохранённый access-токен — опционально вызвать `GET /api/auth/me/` с заголовком `Authorization: Bearer <access_token>`.  
   При 200 — считать пользователя авторизованным и подставить данные в стейт.  
   При 401 — попробовать refresh (как в п.3); при неудаче — очистить токены и показать экран входа.

6. **CORS**  
   Бэкенд уже настроен на разрешённые origins (например `http://localhost:3000`).  
   Запросы с заголовком `Authorization` разрешены.  
   Если фронт на другом origin — добавить его в `CORS_ALLOWED_ORIGINS` на бэкенде.

7. **Формат запросов**  
   Все тела запросов — JSON (`Content-Type: application/json`).  
   Ответы — JSON.

## Тестовый пользователь (после создания на бэкенде)

Чтобы проверить работу:

- Логин: `phil_demo`  
- Пароль: `PhilDemo2026`  

Создать пользователя на бэкенде:  
`python manage.py create_test_user`  
(или в Docker: `docker-compose exec backend python manage.py create_test_user`).

После этого можно проверить логин с фронта или curl:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"phil_demo","password":"PhilDemo2026"}'
```

Ожидается ответ с полями `access`, `refresh` и `user`.
