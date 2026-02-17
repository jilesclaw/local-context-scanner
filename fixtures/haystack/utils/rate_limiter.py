from time import time

class RateLimiter:
    """
    A simple Token Bucket rate limiter.
    Usage:
    limiter = RateLimiter(max_tokens=10, refill_rate=1)
    if limiter.check("user_123"):
        # Allow
    else:
        # Block
    """
    def __init__(self, max_tokens, refill_rate):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = {}

    def check(self, key):
        # ... logic not implemented for brevity in test ...
        return True
