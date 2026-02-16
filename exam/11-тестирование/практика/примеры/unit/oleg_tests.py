import re
from datetime import datetime
import pytest


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> dict:
    errors = []
    if len(password) < 8:
        errors.append("too_short")
    if not re.search(r'[A-Z]', password):
        errors.append("no_uppercase")
    if not re.search(r'[a-z]', password):
        errors.append("no_lowercase")
    if not re.search(r'\d', password):
        errors.append("no_digit")
    if not re.search(r'[!@#$%^&*]', password):
        errors.append("no_special")
    return {"valid": len(errors) == 0, "errors": errors}


def validate_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False


@pytest.mark.parametrize("password, error", [
    ("Ab1!abc", "too_short"),
    ("password1!", "no_uppercase"),
    ("PASSWORD1!", "no_lowercase"),
    ("Password!!", "no_digit"),
    ("Password12", "no_special")
])
def test_validate_password_reports_expected_error(password, error):
    result = validate_password(password)
    assert not result["valid"]
    assert error in result["errors"]


def test_validate_password_accepts_valid():
    result = validate_password("Password12!")
    assert result["valid"] is True
    assert result["errors"] == []


@pytest.mark.parametrize("email, expected", [
    ("stepan.kalimullin@gmail.com", True),
    ("user@domain.co.uk", True),
    ("invalid", False),
    ("@nodomain.com", False),
    ("noatsign.com", False),
])
def test_validate_email(email, expected):
    assert validate_email(email) is expected


@pytest.mark.parametrize("date_str, expected", [
    ("2026-04-21", True),
    ("2000-01-01", True),
    ("not-a-date", False),
    ("2026-13-01", False),
    ("", False),
])
def test_validate_date(date_str, expected):
    assert validate_date(date_str) is expected
