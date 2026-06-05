class FixedWindowLimiter:
    def __init__(self, limit, window_seconds):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._state = {}

    def allow(self, key, timestamp):
        window = int(timestamp // self.window_seconds)
        current_window, count = self._state.get(key, (window, 0))
        if current_window != window:
            current_window, count = window, 0
        if count >= self.limit:
            self._state[key] = (current_window, count)
            return False
        self._state[key] = (current_window, count + 1)
        return True
