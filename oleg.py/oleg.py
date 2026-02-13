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


@pytest.mark.parametrize("password, expected", [
    ("123", "too_short"),
    ("sdfsdfsfs", "no_uppercase"),
    ("QQQQQQ", "no_lowercase"),
    ("fsdfsdf", "no_digit"),
    ("sdfsdfsfds", "no_special")
])
def test_validate_password(password, expected):
    errors = validate_password(password)["errors"]
    assert expected in errors


def test_accept_password():
    assert validate_password("12312!3Qq")["valid"] == True
