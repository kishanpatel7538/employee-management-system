"""Reusable server-side validation helpers for the HRMS."""
import re
from decimal import Decimal, InvalidOperation
from datetime import date

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
PHONE_RE = re.compile(r"^[+0-9() .-]{7,20}$")


def clean_text(value, label, *, required=False, max_length=100):
    value = (value or "").strip()
    if required and not value:
        raise ValueError(f"{label} is required.")
    if len(value) > max_length:
        raise ValueError(f"{label} must be {max_length} characters or fewer.")
    if any(ord(ch) < 32 for ch in value):
        raise ValueError(f"{label} contains invalid characters.")
    return value


def validate_email(value):
    value = clean_text(value, "Email", required=True, max_length=150).lower()
    if not EMAIL_RE.fullmatch(value):
        raise ValueError("Enter a valid email address.")
    return value


def validate_password(value):
    if not value or len(value) < 10:
        raise ValueError("Password must be at least 10 characters long.")
    if len(value) > 128:
        raise ValueError("Password must be 128 characters or fewer.")
    if not re.search(r"[a-z]", value) or not re.search(r"[A-Z]", value) or not re.search(r"\d", value) or not re.search(r"[^A-Za-z0-9]", value):
        raise ValueError("Password must include uppercase, lowercase, a number and a special character.")
    return value


def validate_phone(value):
    value = clean_text(value, "Phone", max_length=20)
    if value and not PHONE_RE.fullmatch(value):
        raise ValueError("Enter a valid phone number (7–20 characters; digits and + ( ) . - only).")
    return value or None


def validate_salary(value, *, required=False):
    value = (value or "").strip()
    if not value:
        if required:
            raise ValueError("Salary is required.")
        return None
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid salary amount.")
    if not amount.is_finite() or amount < 0 or amount > Decimal("9999999999.99"):
        raise ValueError("Salary must be between 0 and 9,999,999,999.99.")
    if amount.as_tuple().exponent < -2:
        raise ValueError("Salary can have no more than two decimal places.")
    return amount


def validate_iso_date(value, label, *, default_today=False):
    value = (value or "").strip()
    if not value and default_today:
        return date.today()
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"Enter a valid {label.lower()}.")
