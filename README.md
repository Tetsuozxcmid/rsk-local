# RSK Local — портал РосДК и микросервисный бэкенд

Каталог `rsk_local` объединяет веб-клиент и серверную часть экосистемы **РосДК**. Публичная продакшен-версия сайта: **[https://rosdk.ru](https://rosdk.ru)**.

## Продакшен: репозитории и инфраструктура

На **проде** используются **отдельные Git-репозитории** для фронтенда и для бэкенда (не один монорепозиторий, как в этой локальной папке). Оба развёрнуты на **выделенном сервере**:

- Трафик **проксируется через [Traefik](https://traefik.io/)** (маршрутизация, TLS-терминация на edge).
- **TLS-сертификаты** выпускаются и продлеваются **[Certbot](https://certbot.eff.org/)** (Let’s Encrypt).
- Сервисы бэкенда и фронт поднимаются в **Docker**; см. также `RSK_back/README.md` и compose-файлы в `RSK_back/`.

Локальная структура здесь повторяет те же проекты для разработки: `rsk_fr-main/` и `RSK_back/`.

---

## Стек и архитектура

### Фронтенд (`rsk_fr-main`)

- **Next.js** 16, **React** 19 — гибрид **SSR/SSG** и клиентская навигация (**SPA-поведение** внутри приложения).
- **JavaScript** и **CSS** (глобальные стили, Tailwind 4 через PostCSS, собственные слои в `src/styles/`).
- **Блочная вёрстка** в рамках компонентов (секции, сетки, layout).
- **Шаблон сайта** свой: кастомные страницы, компоненты и стили, не «голый» стартовый шаблон.
- Запросы к данным: **`fetch` к `/api/...`** (прокси на микросервисы) — по смыслу **AJAX**.
- **Анимации**: **Framer Motion** и связанная логика на стороне клиента.
- **Компонентный подход** и типичные для React **паттерны** (разделение страниц, фич, UI, хелперов, API routes).
- **Авторизация**: интеграция с **OAuth2** (ВК, Яндекс) и **JWT**/сессионные cookie на стороне auth-сервиса; фронт ходит через BFF/API routes.
- **Сборка**: `npm run build` (**автоматическая сборка** Next.js).
- **Стили**: **Tailwind CSS 4** + PostCSS (в учебных критериях часто засчитывают как цепочку препроцессинга CSS; при необходимости уточните у преподавателя относительно формулировки «препроцессор» в духе Sass/Less).
- **Автотесты**: **Vitest** (`npm test`) — см. раздел ниже.

### Бэкенд (`RSK_back`)

- **Асинхронный стек**: **FastAPI** поверх **Starlette**, обработчики на **`async`/`await`**, доступ к БД через **SQLAlchemy 2 async** и драйвер **asyncpg** (в тестах дополнительно используется **aiosqlite** для быстрых проверок без PostgreSQL).
- **Нет CMS** — контент и бизнес-логика в собственных сервисах.
- **REST API** по микросервисам: auth, профиль пользователя, команды, организации, проекты, обучение и др.
- **Динамика сайта**: HTML страниц отдаёт **Next.js**; бэкенд отдаёт **JSON API** (типичная схема для динамического веб-приложения).
- **Документация API**: **OpenAPI** + **Swagger UI** (`/docs`) у сервисов FastAPI.
- **Паттерны**: роутеры, **CRUD**-слои, **сервисы**, HTTP-клиенты к другим микросервисам, события через **RabbitMQ**.
- **Миграции БД**: **Alembic** в сервисах с состоянием.
- **Docker** / **Docker Compose**, описание развёртывания в `RSK_back/README.md`, `RSK_back/LOCAL_DEVELOPMENT.md`.
- **JWT**, **OAuth2** (VK, Яндекс), см. `auth_service`.

---

## Соответствие учебным критериям (шпаргалка)

| Требование | Где в проекте |
|------------|----------------|
| **Front:** блочная вёрстка, JS, CSS, изменённый шаблон | Компоненты + `src/styles` |
| **Front 3:** AJAX, анимации/скрипты, паттерны, компоненты | `fetch`, Framer Motion, структура React |
| **Front 4:** SPA/SSR, сборка, тесты, OAuth2/JWT, фреймворк | Next.js, `npm run build`, Vitest, auth-интеграция, React |
| **Back:** динамика, API, не CMS | Next + JSON API, FastAPI |
| **Back 3:** ≥5 сценариев с клиентом, OpenAPI, паттерны, миграции | Множество API routes и эндпоинтов, Swagger, CRUD/сервисы, Alembic |
| **Back 4:** тесты, методика развёртывания, Docker, общий сервис, фреймворк | pytest, README/compose, Docker, клиенты между сервисами, FastAPI |

---

## Структура каталогов

| Путь | Назначение |
|------|------------|
| `rsk_fr-main/` | Клиент Next.js |
| `RSK_back/` | Микросервисы FastAPI, Docker, Nginx и т.д. |

---

## Локальный запуск

### Бэкенд

```bash
cd RSK_back
docker compose -f docker-compose.local.yml up --build
```

Подробности портов и OAuth: `RSK_back/LOCAL_DEVELOPMENT.md`.

### Фронтенд

```bash
cd rsk_fr-main
npm install
npm run dev
```

Порт по умолчанию задан в `package.json` (например, `1234`).

### Команды в PowerShell (Windows)

В **PowerShell** цепочка **`&&`** как в bash может не работать (зависит от версии). Используйте **точку с запятой**:

```powershell
cd "C:\путь\к\rsk_local\rsk_fr-main"; npm install; npm test
```

Смысл той же «длинной» команды, что и с `&&` в bash:

1. `cd ...` — перейти в папку фронтенда  
2. `npm install` — установить зависимости из `package.json`  
3. `npm test` — запустить скрипт `"test"` (у нас это **Vitest**)

---

## Автотесты

Сводно: **10** тестов в `auth_service`, **10** в `teams_service`, **11** в `user_profile`, **14** на фронте (Vitest). Итого **45** автотестов для отчёта/критериев.

### В Docker (без локального Python 3.12 / npm)

Если на машине **Python 3.14** или неудобный **Node**, тесты можно гонять в контейнерах с теми же версиями, что в прод-образах (**Python 3.11/3.12**, **Node 22**).

Из каталога **`rsk_local`** (рядом с `docker-compose.tests.yml`):

```powershell
# собрать образы и прогнать все четыре набора тестов подряд
.\scripts\run-all-docker-tests.ps1
```

Или по отдельности:

```powershell
cd "C:\путь\к\rsk_local"
docker compose -f docker-compose.tests.yml build
docker compose -f docker-compose.tests.yml run --rm auth_tests
docker compose -f docker-compose.tests.yml run --rm teams_tests
docker compose -f docker-compose.tests.yml run --rm user_profile_tests
docker compose -f docker-compose.tests.yml run --rm frontend_tests
```

На Linux/macOS: `sh scripts/run-all-docker-tests.sh`.

Рабочий **Docker Desktop** (или Docker Engine + compose plugin) обязателен. Тестам **не нужен** запущенный основной `docker-compose` с Postgres: в pytest используется SQLite в памяти; фронт — только `npm ci` + Vitest.

Файлы: `docker-compose.tests.yml`, `rsk_fr-main/Dockerfile.test`, `rsk_fr-main/.dockerignore`.

### Фронтенд (Vitest)

```powershell
cd rsk_fr-main
npm install
npm test
```

Файлы: `src/lib/backendApiBase.test.js` (маршрутизация URL к микросервисам), `src/utils/auth.test.js` (cookie, признак авторизации, сохранение/очистка userData с моками `js-cookie`).

### Бэкенд (pytest)

Установите зависимости сервиса: **`pip install -r requirements.txt`** из каталога сервиса (рекомендуется виртуальное окружение). Для `teams_service` при первом запуске нужен установленный **asyncpg** (он подтягивается из `requirements.txt`).

**Auth** (`RSK_back\auth_service`): JWT, валидация Pydantic, **регистрация и проверка пароля** через `UserCRUD` / `User.check_user` на **SQLite в памяти**; блокировка `pg_advisory` для email подменена в тестах; для стабильности на новых версиях Python в тестах используется **заглушка** вместо bcrypt (логика приложения в проде по-прежнему bcrypt).

```powershell
cd RSK_back\auth_service
python -m pytest tests -q
```

**Teams** (`RSK_back\teams_service`): OpenAPI/metrics, **SQL-операции** с `Team`/`TeamMember` на SQLite, вызовы **хендлеров** маршрутов (`get_teams_count_by_region`, `delete_team`, `get_team_by_id`) с реальной сессией БД. HTTP-клиент к приложению с `root_path="/teams"` в тестах даёт 404 на часть путей, поэтому проверки бизнес-логики идут через **прямой вызов async-функций маршрутов** (эквивалент интеграционного теста без сети).

```powershell
cd RSK_back\teams_service
python -m pytest tests -q
```

**Профиль** (`RSK_back\user_profile`): **смена имени/фамилии/региона** (`ProfileCRUD.update_my_profile`), чтение профиля, вспомогательные функции разбора ФИО и ролей (SQLite + юнит-тесты на чистые методы).

```powershell
cd RSK_back\user_profile
python -m pytest tests -q
```

Во всех трёх каталогах есть **`pytest.ini`** с `asyncio_mode = auto`. Тесты на SQLite **не заменяют** полный прогон против PostgreSQL в Docker, но дают быстрые проверки CRUD и сценариев auth/команд/профиля без поднятия всего стека.

---

## Полезные ссылки

- `RSK_back/README.md` — микросервисы, эндпоинты, Docker  
- `RSK_back/LOCAL_DEVELOPMENT.md` — локальный compose и переменные  
