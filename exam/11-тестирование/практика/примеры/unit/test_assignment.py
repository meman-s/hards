from datetime import datetime
from unittest.mock import MagicMock
from assignment_functions import (
    RateLimiter,
    clamp,
    fetch_user,
    get_current_iso_date,
    is_positive,
    parse_date,
    parse_int,
    process_items,
    safe_divide,
)
import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
@pytest.mark.parametrize("input, result", [
    ("42", 42),
    ("  -7  ", -7),
    ("0", 0)
])
def test_parse_int(input, result):
    assert parse_int(input) == result


@pytest.mark.unit
@pytest.mark.parametrize("input, result", [
    (3, True),
    (-4, False)
])
def test_is_positive(input, result):
    assert is_positive(input) == result


def test_safe_divide_exception():
    with pytest.raises(ValueError, match="division by zero"):
        safe_divide(1, 0)


@pytest.mark.parametrize("a, b, result", [
    (10, 2, 5.0),
    (-1, 4, -0.25)
])
def test_safe_divide(a, b, result):
    assert safe_divide(a, b) == result


def test_parse_date():
    assert type(parse_date("2003-11-21")) == datetime


@pytest.mark.parametrize("value, low, high, result", [
    (5, 6, 7, 6),
    (5, 4, 6, 5),
    (7, 4, 5, 5)
])
def test_clamp(value, low, high, result):
    assert clamp(value, low, high) == result


def test_clamp_exception():
    with pytest.raises(ValueError, match="low must be <= high"):
        clamp(4, 5, 3)


def test_fetch_user():
    mock_get_http = MagicMock()
    mock_get_http.return_value = {"status": 200, "body": {"id": 1, "name": "Stepan"}}

    result = fetch_user(1, mock_get_http)
    assert result == {"id": 1, "name": "Stepan"}
    mock_get_http.assert_called_once_with("/users/1")


def test_fetch_user_exception():
    mock_get_http = MagicMock()
    mock_get_http.return_value = {"status": 400, 'body': "error"}

    with pytest.raises(RuntimeError, match="API error: error"):
        fetch_user(1, mock_get_http)


@patch("assignment_functions.datetime")
def test_assignment_functions(mock_date):
    mock_date.now.return_value = datetime(2025, 6, 15)

    assert get_current_iso_date() == "2025-06-15"
    mock_date.now.assert_called_once()


def test_rate_limiter_allow():
    rl = RateLimiter(max_calls=2, window_seconds=10)
    assert rl.allow(100)
    assert rl.allow(101)
    assert rl.allow(101) is False

    rl_short = RateLimiter(1, 5)
    assert rl_short.allow(100)
    assert rl_short.allow(104) is False
    assert rl_short.allow(106)

    with pytest.raises(ValueError, match="max_calls >= 1 and window_seconds > 0"):
        rl_short = RateLimiter(0, 5)


@pytest.mark.parametrize("items, filter_fn, sort_key, result", [
    ([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 1, lambda y: y, [1, 3, 5]),
    ([3, 1, 2], None, lambda y: -y, [3, 2, 1]),
])
def test_process_items(items, filter_fn, sort_key, result):
    assert process_items(items, filter_fn, sort_key) == result
