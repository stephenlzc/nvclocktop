from datetime import datetime
from argparse import Namespace

import pytest

from gpu_clock import layout
from gpu_clock.gpu import GpuInfo
from gpu_clock.layout import _format_time


def test_format_time_uses_12_hour_clock_with_leading_zero():
    now = datetime(2026, 5, 14, 7, 20, 9)
    assert _format_time(now, "12h", show_seconds=False) == "07:20 AM"


def test_format_time_can_show_seconds():
    now = datetime(2026, 5, 14, 19, 20, 9)
    assert _format_time(now, "12h", show_seconds=True) == "07:20:09 PM"
    assert _format_time(now, "24h", show_seconds=True) == "19:20:09"


@pytest.mark.parametrize("width", [80, 120])
@pytest.mark.parametrize("show_help", [False, True])
def test_snapshot_passes_glyph_boundaries_to_clock_coloring(monkeypatch, width, show_help):
    calls = []
    original = layout.clock_text

    def capture(art, theme, widths):
        calls.append(widths)
        return original(art, theme, widths)

    monkeypatch.setattr(layout, "clock_text", capture)
    args = Namespace(clock="12h", show_seconds=True, font="terrace", theme="rainbow")
    layout.build_snapshot(args, None, GpuInfo(False, None, [], []), show_help, width, 40)
    assert len(calls) == 1
    assert len(calls[0]) == len("10:44:34 AM")
