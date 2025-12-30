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


def to_utc(dt: datetime) -> datetime:
    """
    Convert datetime to UTC.

    Args:
        dt: Datetime (naive or aware)

    Returns:
        Timezone-aware datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
