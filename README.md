# Сервис бронирования переговорных комнат

Веб-сервис для автоматизации бронирования переговорных комнат в коворкинге. Реализован на FastAPI с использованием PostgreSQL и JWT-аутентификации.

## Возможности

- Просмотр доступности комнат на конкретную дату
- Создание и отмена бронирований (сотрудники — только своих, администраторы — любых)
- Управление комнатами и временными слотами
- Разделение ролей: `admin` и `employee`
- Аутентификация через JWT-токены

## Технологии

- **Python** 3.12+
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** 2.0 (async) — работа с базой данных
- **PostgreSQL** — хранилище данных
- **Alembic** — миграции базы данных
- **pytest** — тестирование
- **Docker** — контейнеризация
- **Poetry** — управление зависимостями

## Структура проекта

```
src/
├── api/                 # Роутеры FastAPI
├── data_mappers/        # Мапперы для преобразования данных
├── db/                  # Подключение к БД и менеджер
├── migrations/          # Миграции Alembic
├── models/              # Модели SQLAlchemy
├── repos/               # Репозитории (слой доступа к данным)
├── schemas/             # Pydantic-схемы
├── scripts/             # Служебные скрипты (создание админа)
├── services/            # Бизнес-логика
├── tests/               # Тесты (unit и integration)
└── utils/               # Утилиты (enum, исключения)
```

## Быстрый запуск (Docker)

### Предварительные требования

- Docker и Docker Compose
- Git

### Шаги

1. **Клонируйте репозиторий**
   ```bash
   git clone https://gitlab.com/goormany-group/BookingRoomsService.git
   cd BookingRoomsService
   ```

2. **Настройте переменные окружения**
   ```bash
   cp .env.example .env
   ```
   При необходимости отредактируйте `.env`, особенно секретный ключ JWT.
   Для тестов создайте файл `.env.test`:
   ```bash
   cp .env.example .env.test
   ```
   В `.env.test` укажите другое имя базы данных (например, `booking_rooms_test_db`).

3. **Запустите сервис и базу данных**
   ```bash
   docker compose up --build
   ```
   Сервис будет доступен по адресу `http://localhost:8000`.
   API документация (Swagger UI) — `http://localhost:8000/docs`.

4. **Проверка работоспособности**
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```
   Ожидаемый ответ:
   ```json
   {"status": true}
   ```

## Локальный запуск (без Docker)

### Предварительные требования

- Python 3.12+
- Poetry
- PostgreSQL 15+

### Шаги

1. **Установите зависимости**
   ```bash
   poetry install
   ```

2. **Настройте переменные окружения**
   ```bash
   cp .env.example .env
   ```
   Убедитесь, что `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` и `DB_NAME` соответствуют вашей локальной базе данных.

3. **Примените миграции**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Запустите приложение**
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
   Или напрямую:
   ```bash
   poetry run python src/main.py
   ```

5. **Проверка работоспособности**
   Откройте в браузере:
   - `http://localhost:8000/api/v1/health/` — статус приложения
   - `http://localhost:8000/docs` — интерактивная документация API

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `MODE` | Режим работы | `LOCAL` |
| `APP_HOST` | Хост FastAPI | `0.0.0.0` |
| `APP_PORT` | Порт FastAPI | `8000` |
| `DB_HOST` | Хост PostgreSQL | `db` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_USER` | Пользователь PostgreSQL | `root` |
| `DB_PASSWORD` | Пароль PostgreSQL | `root` |
| `DB_NAME` | Имя базы данных | `booking_rooms_db` |
| `JWT_SECRET_KEY` | Секретный ключ для JWT | `Команда генерации openssl rand -hex 32` |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh-токена | `7` |

## API Эндпоинты

Все эндпоинты находятся под общим префиксом `/api/v1`.

### Аутентификация

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/auth/register` | Регистрация нового пользователя |
| `POST` | `/auth/login` | Аутентификация пользователя |
| `POST` | `/auth/refresh` | Обновление токенов доступа и рефреш токена |

### Пользователи

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/users/?page=&per_page=` | Список пользователей с пагинацией |
| `GET` | `/users/my` | Данные текущего пользователя |
| `GET` | `/users/{user_id}` | Данные конкретного пользователя  |
| `PATCH` | `/users/{user_id}` | Изменение роли пользователя |
| `PATCH` | `/users/{user_id}/restore` | Восстановление пользователя |
| `DELETE` | `/users/{user_id}`  | Установка статусу is_active=False пользователю |
| `DELETE` | `/users/{user_id}`  | Полное удаление пользователя |

### Комнаты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/rooms/` | Создать комнату |
| `GET` | `/rooms/?page=&per_page=` | Список комнат с пагинацией |
| `GET` | `/rooms/{room_id}` | Получить комнату по ID |
| `GET` | `/rooms/{room_id}/bookings` | Получить бронирования комнаты |
| `PATCH` | `/rooms/{room_id}` | Изменение данных комнаты |
| `DELETE` | `/rooms/{user_id}`  | Полное удаление комнаты |

### Временные слоты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/rooms/{room_id}/slots/` | Создать слот для комнаты |
| `GET` | `/rooms/{room_id}/slots/` | Получить слоты комнаты |

### Бронирования

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/bookings/{room_id}` | Создать бронирование |
| `GET` | `/bookings/?page=&per_page=` | Все бронирования с пагинцией |
| `GET` | `/bookings/{booking_id}` | Бронирование команыт по booking_id |
| `GET` | `/bookings/availability?page=&per_page=&date=` | Бронирование команат по booking_id по дате с пагинацией |
| `GET` | `/bookings/availability/{room_id}?date=` | Бронирование команаты room_id по дате |
| `GET` | `/bookings/my` | Бронирование текущего пользователя |
| `GET` | `/bookings/my/{room_id}` | Бронирование конкретной комнаты текущего пользователя |
| `DELETE` | `/bookings/{booking_id}` | Отменить бронирование |
| `DELETE` | `/bookings/my/{booking_id}` | Отменить свое бронирование |


### Проверка здоровья проекта

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health/` | Проверка работоспособности сервиса |

## Примеры работы с API

### 1. Получение токена (логин)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=secret"
```

Ответ:
```json
{
  "access_token": "eyJ...",
  "refresg_token": "eyJ...",
  "token_type": "bearer"
}
```

### 2. Создание комнаты (с токеном admin)

```bash
curl -X POST "http://localhost:8000/api/v1/rooms/" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Переговорная А"}'
```

### 3. Создание временного слота

```bash
curl -X POST "http://localhost:8000/api/v1/rooms/1/slots/" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"start": "09:00", "end": "18:00"}'
```

### 4. Проверка доступности

```bash
curl -X GET "http://localhost:8000/api/v1/bookings/availability?date=2026-07-20&page=1&per_page=20" \
  -H "accept: application/json" \
  -H "Authorization: Bearer eyJ...'"
```

### 5. Создание бронирования

```bash
curl -X POST "http://localhost:8000/api/v1/bookings/1" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"booking_date": "2026-07-20", "start_time": "10:00", "end_time": "11:00"}'
```

### 6. Мои бронирования

```bash
curl "http://localhost:8000/api/v1/bookings/" \
  -H "Authorization: Bearer eyJ..."
```

## Разработка

### Запуск тестов

#### Локально

Убедитесь, что запущена тестовая БД с данными из `.env.test`

```bash
poetry run pytest src/tests/unit
poetry run pytest src/tests/integration
```

#### В Docker

```bash
docker compose --env-file .env.test -f docker-compose.test.yml run --rm app pytest -v
```
или
``` bash
docker compose --env-file .env.test -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from app
```

### Создание миграции

```bash
poetry run alembic revision --autogenerate -m "description"
```

Применение миграций:
```bash
poetry run alembic upgrade head
```

### Создание администратора

Локальный запуск
```bash
poetry run python3 -m src.scripts.create_admin
```

Запуск в Docker
``` bash
docker compose exec -it app python3 -m src.scripts.create_admin
```

## Проверка запуска

### Локально

1. Запустите PostgreSQL и создайте базу данных:
   ```bash
   psql -U postgres -c "CREATE DATABASE booking_rooms_db;"
   ```
2. Примените миграции:
   ```bash
   poetry run alembic upgrade head
   ```
3. Запустите сервис:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
4. Проверьте health:
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```
   Должен вернуться `{"status": true}`.

### В Docker

1. Запустите:
   ```bash
   docker compose up --build
   ```
2. Дождитесь запуска контейнеров (healthcheck должен проходить):
   ```bash
   docker compose ps
   ```
3. Проверьте health:
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```