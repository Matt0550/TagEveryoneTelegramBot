import inspect
from functools import wraps
import sentry_sdk
from utils.config import settings

def set_sentry_context(func):
    """
    Decorator to set Sentry user context.
    Expects a 'user' dict in the kwargs of the decorated endpoint function.
    Supports both sync and async endpoints.
    """
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if settings.SENTRY_DSN and user:
                sentry_sdk.set_user({
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                })
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if settings.SENTRY_DSN and user:
                sentry_sdk.set_user({
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                })
            return func(*args, **kwargs)
        return sync_wrapper
