from __future__ import annotations
from collections import deque
from threading import Lock

_LOG_BUFFER_MAX = 1000
_buffer: deque[str] = deque(maxlen=_LOG_BUFFER_MAX)
_lock = Lock()


def push_log(msg: str) -> None:
    with _lock:
        _buffer.append(msg)


def get_logs() -> list[str]:
    with _lock:
        return list(_buffer)


def tail(n: int = 100) -> list[str]:
    with _lock:
        return list(_buffer)[-n:]
