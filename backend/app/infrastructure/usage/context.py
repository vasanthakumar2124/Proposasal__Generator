import contextvars

_org_id: contextvars.ContextVar[str] = contextvars.ContextVar("usage_org_id", default="")
_user_id: contextvars.ContextVar[str] = contextvars.ContextVar("usage_user_id", default="")


def set_usage_context(org_id: str, user_id: str) -> None:
    _org_id.set(org_id or "")
    _user_id.set(user_id or "")


def get_usage_context() -> tuple[str, str]:
    return _org_id.get(), _user_id.get()
