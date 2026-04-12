"""
Переменные окружения для pydantic Settings до импорта приложения.
Каталог app добавляется в PYTHONPATH.
"""

import os
import sys
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))


def _ensure_auth_env():
    defaults = {
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "5432",
        "DB_USER": "test",
        "DB_PASS": "test",
        "DB_NAME": "test",
        "SECRET_KEY": "unit-test-secret-key-minimum-32-characters-long!",
        "ALGORITHM": "HS256",
        "RABBITMQ_URL": "amqp://guest:guest@127.0.0.1:5672/",
        "SMTP_USERNAME": "test",
        "SMTP_PASSWORD": "test",
        "SMTP_PORT": "587",
        "SMTP_SERVER": "localhost",
        "SENDER_EMAIL": "test@example.com",
        "URL_FOR_TOKEN": "http://localhost",
        "AUTH_SERVICE_URL": "http://localhost:8002",
        "VK_APP_ID": "1",
        "VK_APP_SECRET": "vk-secret",
        "VK_REDIRECT_URI": "http://localhost/vk/cb",
        "YANDEX_CLIENT_ID": "yandex-id",
        "YANDEX_CLIENT_SECRET": "yandex-secret",
        "YANDEX_REDIRECT_URI": "http://localhost/yandex/cb",
        "YANDEX_FRONTEND_URL": "http://localhost:3000",
        "FRONTEND_URL": "http://localhost:3000",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


_ensure_auth_env()
