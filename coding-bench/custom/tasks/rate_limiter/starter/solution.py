class FixedWindowLimiter:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.count = 0

    def allow(self, key, timestamp):
        self.count += 1
        return self.count <= self.limit
