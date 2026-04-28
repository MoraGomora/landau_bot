# Landau Bot - Telegram Модератор

Полнофункциональный Telegram бот для модерации групп, построенный на современном фреймворке **aiogram 3.x** с использованием MongoDB и Redis.

> ⚠️ **ОЧЕНЬ ВАЖНО:** Перед запуском бота необходимо переименовать файл `config.toml.example` в `config.toml`. Без этого бот не сможет запуститься!

## 📑 Оглавление

- [🎯 Основной функционал](#-основной-функционал)
- [🏗️ Архитектура проекта](#-архитектура-проекта)
- [📋 Требования](#-требования)
- [🚀 Быстрый старт](#-быстрый-старт)
  - [1. Локальная установка](#1-локальная-установка)
  - [2. Конфигурация](#2-конфигурация)
  - [3. Запуск локально](#3-запуск-локально)
- [🐳 Развертывание с Docker](#-развертывание-с-docker)
  - [1. Требования](#1-требования)
  - [2. Подготовка](#2-подготовка)
  - [3. Запуск](#3-запуск)
  - [4. Полезные команды Docker Compose](#4-полезные-команды-docker-compose)
  - [5. Redis Commander](#5-redis-commander-веб-интерфейс)
- [⚙️ Конфигурация в деталях](#-конфигурация-в-деталях)
- [🔑 Получение токена бота](#-получение-токена-бота)
- [📊 Команды бота](#-команды-бота)
- [🔧 Расширение функционала](#-расширение-функционала)
- [🔄 Фоновые задачи (Workers)](#-фоновые-задачи-workers)
  - [⏰ SimpleWorker - Периодические задачи](#-simpleworker---периодические-задачи)
  - [⏱️ SimpleTaskManager - Отложенные задачи](#️-simpletaskmanager---отложенные-задачи)
- [🧪 Разработка и тестирование](#-разработка-и-тестирование)
- [📚 Зависимости проекта](#-зависимости-проекта)
- [🐛 Решение проблем](#-решение-проблем)
- [📝 Лицензия](#-лицензия)
- [👥 Авторство](#-авторство)
- [🤝 Поддержка](#-поддержка)
- [🔗 Полезные ссылки](#-полезные-ссылки)

---

## 🎯 Основной функционал

### Основные возможности
- **Управление группами** - Отслеживание события добавления/удаления бота в группу
- **Приватные команды** - Отдельные обработчики команд для владельцев и обычных пользователей
- **Локализация** - Поддержка нескольких языков (английский, русский) через Fluent
- **Логирование** - Структурированное логирование с поддержкой JSON и консольного вывода
- **Ограничение частоты** - Встроенная защита от спама с помощью throttling middleware
- **Отслеживание ограничений** - Использование Redis для отслеживания ограниченных пользователей (с fallback на память)
- **Персистентность** - Хранение данных в MongoDB

### Обработчики (Handlers)
- **Group handlers** - Обработчик приветствия, управление жизненным циклом бота в групп
- **Private handlers** - Команды для администраторов и обычных пользователей
- **Admin commands** - `/ping`, `/stats` и другие команды управления
- **Personal commands** - `/start` для пользователей

### Фильтры и разрешения
- `is_admin` - Фильтр для проверки прав администратора
- `is_owner` - Фильтр для проверки владельца бота
- `member_can_restrict` - Проверка прав на ограничение членов
- `chat_type` - Фильтр по типу чата (группа, приватный чат и т.д.)
- `find_usernames` - Поиск упоминаний пользователей

### Middleware (Прослойки)
- **L10nMiddleware** - Добавление локализации в контекст сообщения
- **ThrottlingMiddleware** - Rate limiting для предотвращения спама
- **WeekendMiddleware** - Специальная обработка в выходные дни
- **ContainerMiddleware** - Инъекция зависимостей (DI контейнер)

### Клавиатуры
- **Confirm** - Клавиатура подтверждения действий
- **Pagination** - Навигация по страницам результатов

## 🏗️ Архитектура проекта

```
landau_bot/
├── bot.py                      # Точка входа приложения
├── config_reader.py            # Чтение и валидация конфигурации
├── config.toml                 # Файл конфигурации (локальный)
├── config.toml.example         # Пример конфигурации
├── fluent_loader.py            # Загрузчик локализаций
├── logs.py                     # Конфигурация логирования
├── requirements.txt            # Зависимости
├── pyproject.toml              # Метаданные проекта
├── Dockerfile                  # Docker контейнер
├── docker-compose.yml          # Docker Compose конфигурация
│
├── core/                       # Основной функционал приложения
│   ├── i18n.py                # Интернационализация
│   ├── container/
│   │   ├── app.py             # DI контейнер (AppContainer)
│   └── __init__.py
│
├── handlers/                   # Обработчики команд и событий
│   ├── __init__.py
│   ├── group/                 # Обработчики для групп
│   │   ├── hello.py           # Команда /hello
│   │   ├── bot_lifecycle.py   # События добавления/удаления бота
│   │   ├── all_messages.py    # Обработка всех сообщений
│   │   ├── lifecycle.py       # Другие события жизненного цикла
│   │   └── utils.py
│   └── private/               # Обработчики приватных чатов
│       ├── admin/             # Команды для администраторов
│       │   └── start.py       # Команда /start для владельцев
│       └── personal/          # Команды для обычных пользователей
│           └── start.py       # Команда /start для пользователей
│
├── filters/                   # Пользовательские фильтры
│   ├── chat_type.py           # Проверка типа чата
│   ├── find_usernames.py      # Поиск упоминаний
│   ├── is_admin.py            # Проверка прав администратора
│   ├── is_owner.py            # Проверка владельца бота
│   └── member_can_restrict.py # Проверка прав ограничения
│
├── middlewares/               # Middleware для обработки обновлений
│   ├── container.py           # Инъекция контейнера
│   ├── localization.py        # Локализация
│   ├── throttling.py          # Rate limiting
│   └── weekend.py             # Специальная обработка выходных
│
├── keyboards/                 # Клавиатуры для сообщений
│   ├── confirm.py             # Кнопки подтверждения
│   └── pagination.py          # Навигация по страницам
│
├── models/                    # Модели данных
│   ├── mongo.py               # Базовые модели MongoDB
│   ├── settings.py            # Модель настроек чата
│   ├── time.py                # Модели времени
│   ├── types.py               # Пользовательские типы
│   ├── users.py               # Модель пользователя
│   └── violation.py           # Модель нарушения
│
├── repositories/              # Data Access Layer
│   ├── repos.py               # Координатор репозиториев
│   └── mongo/                 # MongoDB реализация
│       ├── base.py            # Базовый репозиторий
│       └── __init__.py
│
├── services/                  # Бизнес-логика
│   ├── user.py                # Сервис управления пользователями
│   ├── chat_user.py           # Сервис членов чата
│   └── settings.py            # Сервис настроек
│
├── db/                        # Слой доступа к БД
│   ├── cache_storage.py       # Интерфейс кэширования
│   ├── utils.py               # Утилиты БД
│   └── __init__.py
│
├── enums/                     # Перечисления
│   ├── permission.py          # Права доступа
│   └── status.py              # Статусы
│
└── l10n/                      # Локализации (Fluent FTL)
    ├── en.ftl                 # Английский язык
    └── ru.ftl                 # Русский язык
```

## 📋 Требования

- **Python 3.11+**
- **MongoDB** (для хранения данных)
- **Redis** (для отслеживания ограниченных пользователей; опционально локально, рекомендуется для Docker)
- **Docker** (опционально, для развертывания)

## 🚀 Быстрый старт

### 1. Локальная установка

#### 1.1 Клонирование проекта
```bash
git clone https://github.com/MoraGomora/landau_bot.git
cd landau_bot
```

#### 1.2 Создание виртуального окружения
```bash
# Linux/macOS
python3.11 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 1.3 Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Конфигурация

#### 2.1 Копирование примера конфигурации
```bash
cp config.toml.example config.toml
```

#### 2.2 Заполнение конфигурации
Отредактируйте `config.toml`:

```toml
[bot]
# Получите токен у @BotFather в Telegram
token = "YOUR_BOT_TOKEN_HERE"

# ID владельца бота (ваш user ID в Telegram)
owners = [123456789]

[mongodb]
# Данные подключения к MongoDB
username = "your_username"
password = "your_password"
cluster_url = "your_cluster.mongodb.net"
app_name = "landau"

[logs]
show_datetime = true
datetime_format = "%Y-%m-%d %H:%M:%S"
show_debug_logs = true
time_in_utc = false
renderer = "console"  # или "json"
use_colors_in_console = true

[localization]
default_locale = "en"  # или "ru"
fallback_locale = "en"
locales_path = "l10n"

[throttling]
enabled = true
rate_limit = 1  # Секунд между сообщениями
max_users = 100
```

#### 2.3 Использование переменных окружения (альтернатива)
Вместо редактирования файла конфигурации вы можете использовать переменные окружения:

```bash
# Linux/macOS
export BOT_TOKEN="YOUR_BOT_TOKEN"
export BOT_OWNERS="123456789"
export MONGODB_USERNAME="your_username"
export MONGODB_PASSWORD="your_password"
export MONGODB_CLUSTER_URL="your_cluster.mongodb.net"
export REDIS_URL="redis://localhost:6379/0"
export REDIS_PASSWORD="your_redis_password"

# Windows (PowerShell)
$env:BOT_TOKEN="YOUR_BOT_TOKEN"
$env:BOT_OWNERS="123456789"
# и т.д.
```

### 3. Запуск локально

#### 3.1 Убедитесь что работают зависимости
```bash
# Проверка подключения к MongoDB
python -c "from config_reader import get_config, MongoConfig; print('Config loaded successfully')"
```

#### 3.2 Запуск бота
```bash
python bot.py
```

Вывод должен быть похож на:
```
2024-12-20 10:30:45 [INFO] Bot started username=landau_bot bot_id=123456789
```

#### 3.3 Тестирование бота
В Telegram:
1. Напишите боту `/start` - бот ответит приветствием
2. `/ping` - проверка, что бот работает
3. `/stats` - статистика бота
4. `/help` - справка по командам

## 🐳 Развертывание с Docker

### 1. Требования
- Docker и Docker Compose установлены
- Файл `.env` с переменными окружения

### 2. Подготовка

#### 2.1 Создайте файл `.env`
```bash
cp .env.example .env  # Или создайте вручную
```

#### 2.2 Заполните `.env`
```
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
BOT_OWNERS=123456789
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER_URL=your_cluster.mongodb.net
MONGODB_APP_NAME=landau
REDIS_PASSWORD=your_secure_redis_password
TZ=UTC
```

### 3. Запуск

#### 3.1 Начать контейнеры
```bash
docker-compose up -d
```

Это запустит:
- **bot** - сам Telegram бот
- **redis** - Redis для отслеживания ограниченных пользователей
- **redis-commander** - веб-интерфейс для управления Redis (опционально)

> ⚠️ **ВАЖНО:** Redis необходим для нормальной работы бота в режиме Docker. Если Redis недоступен, бот будет использовать in-memory память (данные будут потеряны при перезагрузке контейнера). Убедитесь, что Redis запущен и доступен перед запуском бота!

#### 3.2 Проверка статуса
```bash
docker-compose ps

# Должен быть вывод похожий на:
# NAME                          STATUS
# landau-moder                  Up X minutes
# redis-landau-moder           Up X minutes
# landau-moder-redis-commander Up X minutes
```

#### 3.3 Просмотр логов
```bash
# Логи всех контейнеров
docker-compose logs -f

# Логи только бота
docker-compose logs -f bot

# Последние 100 строк и выход
docker-compose logs --tail=100
```

#### 3.4 Остановка контейнеров
```bash
# Остановка
docker-compose stop

# Полное удаление контейнеров (данные сохраняются в volumes)
docker-compose down

# Удаление всего включая volumes (осторожно!)
docker-compose down -v
```

### 4. Полезные команды Docker Compose

```bash
# Пересборка образа (после изменения зависимостей)
docker-compose build

# Пересборка и перезапуск
docker-compose up -d --build

# Перезагрузка конкретного сервиса
docker-compose restart bot

# Масштабирование (если приложение позволяет)
docker-compose up -d --scale bot=2

# Очистка неиспользуемых образов и контейнеров
docker system prune -a
```

### 5. Redis Commander (веб-интерфейс)

После запуска `docker-compose up -d` Redis Commander доступен по адресу:
- http://localhost:8081

Здесь вы можете:
- Просматривать записи об ограниченных пользователях
- Редактировать ключи
- Проверять использование памяти
- Мониторить состояние кэша ограничений

## ⚙️ Конфигурация в деталях

### Bot конфигурация
```toml
[bot]
token = "BOT_TOKEN"        # Обязательно: токен от @BotFather
owners = [123456789]       # Список ID владельцев бота
```

### MongoDB конфигурация
```toml
[mongodb]
username = "user"          # Имя пользователя MongoDB
password = "pass"          # Пароль
cluster_url = "cluster..."  # URL кластера (без mongodb+srv://)
app_name = "landau"        # Название приложения в MongoDB
```

### Логирование
```toml
[logs]
show_datetime = true              # Показывать дату и время
datetime_format = "%Y-%m-%d %H:%M:%S"  # Формат времени
show_debug_logs = true            # DEBUG уровень логирования
time_in_utc = false               # Использовать UTC
renderer = "console"              # "console" или "json"
use_colors_in_console = true      # Цвета в консоли
```

### Локализация
```toml
[localization]
default_locale = "en"       # Язык по умолчанию
fallback_locale = "en"      # Резервный язык
locales_path = "l10n"       # Папка с переводами
```

### Rate limiting (Throttling)
```toml
[throttling]
enabled = true              # Включен ли лимит
rate_limit = 1              # Секунд между сообщениями
max_users = 100             # Макс пользователей в кэше
```

## 🔑 Получение токена бота

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте `/newbot`
3. Введите имя бота (название, которое будет видно в чатах)
4. Введите юзернейм бота (должен заканчиваться на `_bot`)
5. Скопируйте полученный токен
6. Вставьте в `config.toml` в поле `token`

## 📊 Команды бота

### Для владельцев
- `/start` - Начало работы (вывод приветствия)
- `/ping` - Проверка, что бот работает (ответ "Pong!")
- `/stats` - Статистика работы бота
- `/help` - Справка по командам

### Для всех пользователей
- `/start` - Начало работы

### В группах
- `/hello` - Приветствие от бота (если добавлен в группу)

## 🔧 Расширение функционала

### Добавление новой команды в группу

Создайте файл `handlers/group/my_command.py`:

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router(name="my_command")

@router.message(Command("mycommand"))
async def my_command(msg: Message):
    await msg.answer("Ответ на команду")
```

Затем зарегистрируйте в `handlers/group/__init__.py`.

### Добавление новой команды для владельца

Создайте файл `handlers/private/admin/my_command.py`:

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.container import AppContainer

router = Router(name="my_command")

@router.message(Command("mycommand"))
async def my_command(msg: Message, container: AppContainer):
    await container.logger.ainfo("Command executed", user_id=msg.from_user.id)
    await msg.answer("Ответ для владельца")
```

### Добавление локализации

В файл `l10n/en.ftl` добавьте:
```
my-message = My message in English
```

В файл `l10n/ru.ftl` добавьте:
```
my-message = Мое сообщение на русском
```

Используйте в коде:
```python
message_text = l10n.format_value("my-message")
await msg.answer(message_text)
```

## 🔄 Фоновые задачи (Workers)

**Workers** (воркеры) — это фоновые асинхронные задачи, которые выполняются периодически с заданным интервалом. Они идеально подходят для:
- Периодических проверок (например, статус пользователей)
- Отложенных операций (удаление сообщений через определённое время)
- Мониторинга (проверка подключения к БД)
- Любых повторяющихся задач

### ⏰ SimpleWorker - Периодические задачи

**SimpleWorker** предназначен для выполнения асинхронных функций с постоянным повторением через заданный интервал.

#### Как работают воркеры

Каждый воркер (`SimpleWorker`) запускается в отдельной асинхронной задаче (`asyncio.Task`) и выполняется в цикле:

1. **Инициализация** - воркер создается с функцией для выполнения и интервалом повторения
2. **Регистрация** - воркер регистрируется в `SimpleWorkerManager`
3. **Запуск** - все воркеры запускаются одновременно при старте бота
4. **Цикл выполнения** - воркер выполняет функцию, затем ждёт интервал, затем повторяет
5. **Обработка ошибок** - менеджер ловит исключения и логирует их
6. **Остановка** - все воркеры останавливаются при выключении бота

#### Атрибуты SimpleWorker

| Атрибут | Тип | Описание |
|---------|-----|---------|
| `_name` | `str` | Уникальное имя воркера (используется для идентификации и логирования) |
| `_func` | `Callable[[], Awaitable[None]]` | Асинхронная функция, которую выполняет воркер |
| `_interval` | `int` | Интервал повторения в секундах (время ожидания между выполнениями) |
| `_lock` | `asyncio.Lock` | Блокировка для синхронизации (по умолчанию новая Lock, но можно передать свою для координации между воркерами. Если вы передаёте свой Lock - рекомендуется его создать в `AppContainer`, чтобы один и тот же блокировщик был доступен с любой точки бота) |
| `_task` | `asyncio.Task \| None` | Текущая задача asyncio (устанавливается при запуске) |

#### Как подключать воркеры

##### Вариант 1: Через менеджер (рекомендуется) ✅

```python
from core import SimpleWorker

def register_tasks(bot: Bot, container: AppContainer):
    # Создаём и регистрируем воркер через менеджер
    container.worker_manager.register(
        SimpleWorker(
            name="my-task",                    # Уникальное имя
            func=lambda: my_async_function,    # Функция для выполнения
            interval=30,                       # Интервал в секундах
            lock=container.some_lock           # (Опционально) Shared lock
        )
    )

async def on_startup(bot: Bot, container: AppContainer):
    register_tasks(bot, container)
    container.worker_manager.start_all()    # Запуск всех воркеров
```

> ⚠️ **ВАЖНО:** Всегда создавайте воркеры через `SimpleWorkerManager`, так как это обеспечивает:
> - **Обработку ошибок** — менеджер ловит исключения и логирует их
> - **Координацию** — безопасное управление всеми воркерами
> - **Логирование** — автоматическое логирование старта, остановки и сбоев
> - **Синхронизацию** — корректная работа с блокировками

##### Вариант 2: Прямое использование (не рекомендуется) ❌

```python
# Это не рекомендуется, так как нет обработки ошибок, из-за чего воркер при ошибке просто перестанет работать!
worker = SimpleWorker("my-task", my_function, 30)
task = worker.start()  # Без контроля менеджера
```

#### Пример: Создание простого воркера

```python
# tasks.py или в коде bot.py
async def check_user_status(bot: Bot, container: AppContainer):
    """Периодическая проверка статуса пользователей."""
    try:
        # Ваша логика проверки
        users = await container.services.user.get_all_active()
        
        for user in users:
            # Обновление статуса
            await container.services.user.update_status(user.id, "online")
        
        await container.logger.ainfo("User status check completed", count=len(users))
    except Exception as e:
        await container.logger.aerror("User status check failed", error=str(e))

def register_tasks(owners: list, bot: Bot, container: AppContainer):
    # Регистрация воркера через менеджер
    container.worker_manager.register(
        SimpleWorker(
            "check-user-status",
            lambda: check_user_status(bot, container),
            interval=60,                    # Проверяем каждые 60 секунд
            lock=container.ban_member_lock  # Используем существующую блокировку
        )
    )

async def on_startup(owners: list, bot: Bot, container: AppContainer, logger: FilteringBoundLogger):
    register_tasks(owners, bot, container)
    container.worker_manager.start_all()   # Запуск всех воркеров (по умолчанию уже прописано)
    # ... остальной код
```

#### Пример: Синхронизация между воркерами

Если нужно, чтобы два воркера не выполнялись одновременно, используйте общую `asyncio.Lock`:

```python
# В AppContainer создаёте общую блокировку
shared_lock = asyncio.Lock()

# Регистрируете оба воркера с одной блокировкой
container.worker_manager.register(
    SimpleWorker("task-1", task_1_func, 30, lock=shared_lock)
)
container.worker_manager.register(
    SimpleWorker("task-2", task_2_func, 45, lock=shared_lock)
)
```

### ⏱️ SimpleTaskManager - Отложенные задачи

`SimpleTaskManager` предназначен для выполнения асинхронных функций с **определённой задержкой** (в отличие от воркеров, которые выполняются в цикле). Это удобно для одноразовых отложенных операций.

#### Основные различия между SimpleWorker и SimpleTaskManager

| Характеристика | SimpleWorker | SimpleTaskManager |
|---|---|---|
| **Тип выполнения** | Циклическое (повторяется) | Одноразовое (с задержкой) |
| **Интервал** | Постоянный интервал | Фиксированная задержка перед выполнением |
| **Использование** | Мониторинг, периодические проверки | Отложенные действия (удаление сообщений, отправка напоминаний) |
| **Менеджер** | SimpleWorkerManager | SimpleTaskManager |

#### Методы SimpleTaskManager

| Метод | Параметры | Описание |
|-------|-----------|---------|
| `shedule(name, func, delay)` | `name: str` - уникальное имя<br>`func: Callable` - асинхронная функция<br>`delay: int` - задержка в секундах | Создаёт задачу с задержкой. Если задача с таким именем уже существует, она отменяется и создаётся новая |
| `cancel(name)` | `name: str` - имя задачи | Отменяет конкретную задачу по имени |
| `cancel_all()` | — | Отменяет все активные задачи |

#### Как работает SimpleTaskManager

1. **Создание задачи** — вызовите `schedule(name, func, delay)`
2. **Задержка** — функция ждёт `delay` секунд
3. **Выполнение** — после задержки функция выполняется
4. **Обработка ошибок** — если функция выбросит исключение, оно логируется
5. **Очистка** — после выполнения задача удаляется из менеджера

#### Пример: Удаление сообщения через время

```python
from core.container import AppContainer

async def delete_message_after_delay(message_id: int, chat_id: int, container: AppContainer):
    """Удалить сообщение через определённое время."""
    try:
        await container.bot.delete_message(chat_id, message_id)
        await container.logger.ainfo(
            "Message deleted",
            message_id=message_id,
            chat_id=chat_id
        )
    except Exception as e:
        await container.logger.aerror(
            "Failed to delete message",
            message_id=message_id,
            chat_id=chat_id,
            error=str(e)
        )

# В обработчике команды
async def cmd_temp_message(msg: Message, container: AppContainer):
    """Отправить временное сообщение, которое удалится через 30 секунд."""
    temp_msg = await msg.answer("Это временное сообщение! 🕐")
    
    # Планируем удаление через 30 секунд
    container.task_manager.shedule(
        name=f"delete-msg-{temp_msg.message_id}",
        func=lambda: delete_message_after_delay(temp_msg.message_id, msg.chat.id, container),
        delay=30
    )
```

#### Пример: Отправка напоминания пользователю

```python
async def send_reminder(user_id: int, text: str, bot: Bot, container: AppContainer):
    """Отправить напоминание пользователю."""
    try:
        await bot.send_message(user_id, f"📢 Напоминание: {text}")
        await container.logger.ainfo("Reminder sent", user_id=user_id)
    except Exception as e:
        await container.logger.aerror("Failed to send reminder", user_id=user_id, error=str(e))

# В обработчике
async def cmd_remind(msg: Message, container: AppContainer, bot: Bot):
    """Установить напоминание на 5 минут."""
    user_id = msg.from_user.id
    reminder_text = "Не забудьте выполнить задачу!"
    
    # Планируем напоминание через 300 секунд (5 минут)
    container.task_manager.shedule(
        name=f"reminder-{user_id}",
        func=lambda: send_reminder(user_id, reminder_text, bot, container),
        delay=300  # 5 минут в секундах
    )
    
    await msg.answer("⏰ Напоминание установлено на 5 минут!")
```

#### Пример: Замена одной задачи на другую

```python
# Первая попытка напоминания
container.task_manager.shedule(
    name="user-reminder",  # Уникальное имя
    func=lambda: send_reminder(user_id, "Первое напоминание", bot, container),
    delay=60
)

# Если пользователь нажал кнопку "Отложить", отменяем старое и создаём новое
container.task_manager.shedule(
    name="user-reminder",  # То же имя - старая задача отменится
    func=lambda: send_reminder(user_id, "Отложенное напоминание", bot, container),
    delay=600  # Новая задержка 10 минут
)
```

> 💡 **Совет:** Используйте уникальные имена в формате `entity-action-id` (например: `delete-msg-123`, `user-reminder-456`), чтобы легко управлять задачами по смыслу.

#### Пример: Отмена задачи

```python
# Отменить одну задачу
if user_agreed:
    container.task_manager.cancel(f"warning-message-{user_id}")
    await msg.answer("✅ Напоминание отменено!")

# Отменить все задачи
async def on_shutdown(container: AppContainer):
    container.task_manager.cancel_all()
    await container.logger.ainfo("All scheduled tasks cancelled")
```

## 🧪 Разработка и тестирование

### Установка зависимостей для разработки

```bash
pip install -e ".[dev]"
```

Это установит дополнительные инструменты:
- `ruff` - линтер и форматер кода
- `mypy` - проверка типов
- `pytest` - фреймворк для тестов
- `pytest-asyncio` - поддержка асинхронных тестов

### Проверка кода

```bash
# Проверка стиля кода
ruff check .

# Исправление автоматических ошибок
ruff check --fix .

# Проверка типов
mypy bot.py core/ handlers/ models/ services/ repositories/

# Форматирование кода
ruff format .
```

### Запуск тестов

```bash
pytest
pytest -v  # Подробный вывод
pytest -s  # С выводом print()
```

## 📚 Зависимости проекта

### Основные
- **aiogram (>=3.4.0)** - Фреймворк для Telegram ботов
- **aiohttp (>=3.9.0)** - Асинхронный HTTP клиент
- **structlog (>=24.0.0)** - Структурированное логирование
- **pydantic (>=2.0.0)** - Валидация данных
- **pydantic-settings (>=2.0.0)** - Управление конфигурацией
- **fluent.runtime (>=0.4.0)** - Локализация (runtime)
- **fluent.syntax (>=0.19.0)** - Парсинг Fluent файлов
- **cachetools (>=5.0.0)** - Инструменты кэширования
- **redis (>=5.0.0)** - Клиент для Redis
- **motor (>=3.x)** - Асинхронный драйвер MongoDB

### Опциональные
- **pytest** - Фреймворк для тестирования
- **mypy** - Проверка типов
- **ruff** - Линтер и форматер

## 🐛 Решение проблем

### Проблема: "Failed to connect to MongoDB"
**Решение:**
1. Проверьте, что MongoDB запущена и доступна
2. Проверьте учетные данные в `config.toml`
3. Если используете MongoDB Atlas, добавьте IP адрес вашей машины в Network Settings

### Проблема: Бот не отвечает на команды
**Решение:**
1. Проверьте токен бота в `config.toml`
2. Проверьте логи: `docker-compose logs bot`
3. Убедитесь, что бот добавлен в чат (для групп)
4. Проверьте, что у вас нет rate limiting проблем

### Проблема: Redis не подключается
**Решение:**
1. Проверьте, что Redis запущен: `docker-compose ps`
2. Проверьте переменную `REDIS_URL` в `.env`
3. Проверьте пароль Redis: `REDIS_PASSWORD`
4. Посмотрите логи Redis: `docker-compose logs redis`

### Проблема: Логирование не работает
**Решение:**
1. Проверьте настройку `renderer` в `[logs]` секции
2. Попробуйте переключиться между `"console"` и `"json"`
3. Проверьте, что директория логов доступна для записи
4. Убедитесь, что `show_debug_logs = true` для DEBUG сообщений
5. Если вы работаете на Windows и у вас включено отображение цветных логов - установите дополнительно `colorama`

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE) файл для деталей

## 👥 Авторство

Разработано: MoraGomora (Modaxon)

За основу был взят [вот этот шаблон](https://github.com/Priler/tgbotbase3)

Этот README был создан с помощью Copilot

## 🤝 Поддержка

Если у вас есть вопросы или проблемы:
1. Проверьте раздел "Решение проблем" выше
2. Посмотрите существующие issues на GitHub
3. Создайте новый issue с описанием проблемы

## 🔗 Полезные ссылки

- [Документация aiogram](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MongoDB документация](https://docs.mongodb.com/)
- [Redis документация](https://redis.io/documentation)
- [Project Fluent](https://projectfluent.org/)

---

**Последнее обновление:** Апрель 2026
