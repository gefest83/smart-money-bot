from __future__ import annotations
import time
import functools
import random
from typing import Callable


def retry(exceptions: tuple = (Exception,), tries: int = 4, delay: float = 1.0, backoff: int = 2):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    time.sleep(_delay + random.random() * 0.1)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator
