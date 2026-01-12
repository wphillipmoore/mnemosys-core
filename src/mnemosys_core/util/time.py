"""
UTC-only time helpers.
"""

from datetime import UTC, date, datetime


def utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Timezone-aware datetime in UTC
    """
    return datetime.now(UTC)


def today_utc() -> date:
    """
    Get current UTC date.

    Returns:
        Date in UTC timezone
    """
    return utc_now().date()


def to_utc(datetime_value: datetime) -> datetime:
    """
    Convert datetime to UTC.

    Args:
        datetime_value: Datetime (naive or aware)

    Returns:
        Timezone-aware datetime in UTC
    """
    if datetime_value.tzinfo is None:
        # Assume naive datetime is UTC
        return datetime_value.replace(tzinfo=UTC)
    return datetime_value.astimezone(UTC)
