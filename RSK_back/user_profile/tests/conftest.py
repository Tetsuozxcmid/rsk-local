import os
import sys
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))


def _ensure_profile_env():
    defaults = {
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "5432",
        "DB_USER": "test",
        "DB_PASS": "test",
        "DB_NAME": "test",
        "RABBITMQ_URL": "amqp://guest:guest@127.0.0.1:5672/",
        "SECRET_KEY": "unit-test-secret-key-minimum-32-characters-long!",
        "ALGORITHM": "HS256",
        "ORGS_URL": "http://localhost:8005",
        "AUTH_SERVICE_URL": "http://localhost:8002",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


_ensure_profile_env()
