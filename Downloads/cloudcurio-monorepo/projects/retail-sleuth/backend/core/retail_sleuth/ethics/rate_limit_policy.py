#!/usr/bin/env python3
'''Simple token-bucket style rate limiting policy (local only).'''

import time
from dataclasses import dataclass

@dataclass
class RateLimitPolicy:
    '''In-memory rate limit policy for a single process.'''
    max_requests_per_minute: int
    _tokens: float = 0.0
    _last_refill: float = 0.0

    def allow(self) -> bool:
        '''Return True if a request is allowed, False otherwise.'''
        now = time.time()
        if self._last_refill == 0.0:
            self._last_refill = now
            self._tokens = self.max_requests_per_minute

        # Refill at 1/60 of max per second
        elapsed = now - self._last_refill
        refill = elapsed * (self.max_requests_per_minute / 60.0)
        self._tokens = min(self.max_requests_per_minute, self._tokens + refill)
        self._last_refill = now

        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False
