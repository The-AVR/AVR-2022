import functools
from typing import Any, Callable

from loguru import logger


def try_except(reraise: bool = False) -> Callable:
    """
    Function decorator that acts as a try/except block around the function.

    Effectively equivalent to:

    ```python
    try:
        func()
    except Exception as e:
        print(e)
    ```

    Can optionally reraise the exception.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Unexpected exception in {func.__name__}")
                if reraise:
                    raise e from e

        return wrapper

    return decorator


def async_try_except(reraise: bool = False) -> Callable:
    """
    Same as `try_except()` function, just for async functions.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Unexpected exception in {func.__name__}")
                if reraise:
                    raise e from e

        return wrapper

    return decorator
