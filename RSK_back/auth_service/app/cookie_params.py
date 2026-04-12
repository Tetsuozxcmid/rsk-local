"""Central auth cookie flags for HTTP vs HTTPS and optional Domain (localhost vs .rosdk.ru)."""
from typing import Any, Dict, Optional

from config import settings


def resolved_cookie_domain() -> Optional[str]:
    raw = (getattr(settings, "COOKIE_DOMAIN", "") or "").strip()
    if not raw:
        return None
    return raw


def session_set_cookie_kwargs(*, max_age: Optional[int] = None) -> Dict[str, Any]:
    secure = bool(getattr(settings, "COOKIE_SECURE", True))
    kw: Dict[str, Any] = {
        "path": "/",
        "httponly": True,
        "secure": secure,
        "samesite": "none" if secure else "lax",
    }
    dom = resolved_cookie_domain()
    if dom:
        kw["domain"] = dom
    if max_age is not None:
        kw["max_age"] = max_age
    return kw


def session_delete_cookie_kwargs() -> Dict[str, Any]:
    secure = bool(getattr(settings, "COOKIE_SECURE", True))
    kw: Dict[str, Any] = {
        "path": "/",
        "httponly": True,
        "secure": secure,
        "samesite": "none" if secure else "lax",
    }
    dom = resolved_cookie_domain()
    if dom:
        kw["domain"] = dom
    return kw


def userdata_delete_cookie_kwargs() -> Dict[str, Any]:
    """Matches previous behaviour for the non-HttpOnly userData cookie."""
    secure = bool(getattr(settings, "COOKIE_SECURE", True))
    kw: Dict[str, Any] = {
        "path": "/",
        "secure": secure,
        "samesite": "none" if secure else "lax",
    }
    dom = resolved_cookie_domain()
    if dom:
        kw["domain"] = dom
    return kw
