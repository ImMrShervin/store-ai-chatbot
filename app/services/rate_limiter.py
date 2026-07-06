import time
import threading
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_per_minute: int = 20):
        self.max = max_per_minute
        self.window = 60.0
        self._store: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            q = self._store[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.max:
                retry = int(self.window - (now - q[0])) + 1
                return False, retry
            q.append(now)
            return True, 0
