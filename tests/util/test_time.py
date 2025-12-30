"""
Time utility tests.
"""

from datetime import UTC, datetime, timezone

from mnemosys_core.util.time import to_utc, today_utc, utc_now


def test_utc_now() -> None:
    """Test utc_now returns timezone-aware UTC datetime."""
    result = utc_now()

    assert isinstance(result, datetime)
    assert result.tzinfo == UTC
    # Should be close to actual current time (within 1 second)
    now = datetime.now(UTC)
    assert abs((now - result).total_seconds()) < 1


def test_today_utc() -> None:
    """Test today_utc returns current UTC date."""
    result = today_utc()

    expected = datetime.now(UTC).date()
    assert result == expected


def test_to_utc_with_naive_datetime() -> None:
    """Test to_utc with naive datetime assumes UTC."""
    naive_dt = datetime(2025, 1, 15, 10, 30, 0)

    result = to_utc(naive_dt)

    assert result.tzinfo == UTC
    assert result.year == 2025
    assert result.month == 1
    assert result.day == 15
    assert result.hour == 10
    assert result.minute == 30


def test_to_utc_with_aware_datetime_utc() -> None:
    """Test to_utc with already UTC datetime."""
    utc_dt = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

    result = to_utc(utc_dt)

    assert result.tzinfo == UTC
    assert result == utc_dt


def test_to_utc_with_aware_datetime_other_timezone() -> None:
    """Test to_utc converts other timezones to UTC."""
    from datetime import timedelta

    # Create a datetime in EST (UTC-5)
    est = timezone(timedelta(hours=-5))
    est_dt = datetime(2025, 1, 15, 10, 30, 0, tzinfo=est)

    result = to_utc(est_dt)

    assert result.tzinfo == UTC
    # 10:30 EST should be 15:30 UTC
    assert result.hour == 15
    assert result.minute == 30


def test_to_utc_preserves_date_components() -> None:
    """Test to_utc preserves date for naive datetimes."""
    naive_dt = datetime(2025, 12, 31, 23, 59, 59)

    result = to_utc(naive_dt)

    assert result.year == 2025
    assert result.month == 12
    assert result.day == 31
    assert result.hour == 23
    assert result.minute == 59
    assert result.second == 59
