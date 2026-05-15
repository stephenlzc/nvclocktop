from datetime import datetime

from gpu_clock.layout import _format_time


def test_format_time_uses_12_hour_clock_with_leading_zero():
    now = datetime(2026, 5, 14, 7, 20, 9)
    assert _format_time(now, "12h", show_seconds=False) == "07:20 AM"


def test_format_time_can_show_seconds():
    now = datetime(2026, 5, 14, 19, 20, 9)
    assert _format_time(now, "12h", show_seconds=True) == "07:20:09 PM"
    assert _format_time(now, "24h", show_seconds=True) == "19:20:09"
