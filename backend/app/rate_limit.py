from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic


class InMemoryRateLimiter:
    """Demo-only limiter; replace with an infrastructure adapter before public scale-out."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        threshold = now - self._window_seconds
        bucket = self._requests[key]
        while bucket and bucket[0] <= threshold:
            bucket.popleft()
        if len(bucket) >= self._max_requests:
            return False
        bucket.append(now)
        return True
