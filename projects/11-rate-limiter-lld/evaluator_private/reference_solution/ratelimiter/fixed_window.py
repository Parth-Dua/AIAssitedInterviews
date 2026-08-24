"""Reference solution — FixedWindowRateLimiter."""

import time
from dataclasses import dataclass
from typing import Callable, Dict

from .base import RateLimiter


@dataclass
class _WindowState:
    window_index: int
    count: int


class FixedWindowRateLimiter(RateLimiter):
    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        now_fn: Callable[[], float] = time.monotonic,
    ):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._now_fn = now_fn
        self._windows: Dict[str, _WindowState] = {}

    def _current_window_index(self, now: float) -> int:
        return int(now // self._window_seconds)

    def allow_request(self, key: str) -> bool:
        now = self._now_fn()
        current_index = self._current_window_index(now)

        state = self._windows.get(key)
        if state is None or state.window_index != current_index:
            state = _WindowState(window_index=current_index, count=0)
            self._windows[key] = state

        if state.count < self._max_requests:
            state.count += 1
            return True
        return False
