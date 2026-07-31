import logging
from functools import wraps
from time import perf_counter
from typing import Callable, Any

logger = logging.getLogger("proposalcraft")


def log_execution_time(func: Callable) -> Callable:
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = perf_counter() - start
            logger.debug("%s took %.3fs", func.__name__, elapsed)
            return result
        except Exception as e:
            elapsed = perf_counter() - start
            logger.error("%s failed after %.3fs: %s", func.__name__, elapsed, str(e))
            raise

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = perf_counter() - start
            logger.debug("%s took %.3fs", func.__name__, elapsed)
            return result
        except Exception as e:
            elapsed = perf_counter() - start
            logger.error("%s failed after %.3fs: %s", func.__name__, elapsed, str(e))
            raise

    if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
        return async_wrapper
    return sync_wrapper
