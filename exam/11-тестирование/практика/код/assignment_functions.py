import re
from datetime import datetime
from typing import Callable, Optional


def parse_int(value: str) -> int:
    return int(value.strip())


def is_positive(n: int) -> bool:
    return n > 0


def format_name(first: str, last: str) -> str:
    return f"{last}, {first}".strip()


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s.strip("-")


def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> Optional[datetime]:
    try:
        return datetime.strptime(date_str.strip(), fmt)
    except ValueError:
        return None


def clamp(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(high, value))


def get_current_iso_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def fetch_user(user_id: int, get_http) -> dict:
    response = get_http(f"/users/{user_id}")
    if response.get("status") != 200:
        raise RuntimeError(f"API error: {response.get('body', '')}")
    return response.get("body", {})


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float):
        if max_calls < 1 or window_seconds <= 0:
            raise ValueError("max_calls >= 1 and window_seconds > 0")
        self._max_calls = max_calls
        self._window = window_seconds
        self._calls = []

    def _trim_old(self, now: float) -> None:
        cutoff = now - self._window
        self._calls = [t for t in self._calls if t > cutoff]

    def allow(self, now: Optional[float] = None) -> bool:
        if now is None:
            now = datetime.now().timestamp()
        self._trim_old(now)
        if len(self._calls) >= self._max_calls:
            return False
        self._calls.append(now)
        return True

    def remaining(self, now: Optional[float] = None) -> int:
        if now is None:
            now = datetime.now().timestamp()
        self._trim_old(now)
        return max(0, self._max_calls - len(self._calls))


def process_items(
    items: list,
    filter_fn: Optional[Callable] = None,
    sort_key: Optional[Callable] = None,
) -> list:
    if filter_fn is not None:
        items = [x for x in items if filter_fn(x)]
    if sort_key is not None:
        items = sorted(items, key=sort_key)
    return items
