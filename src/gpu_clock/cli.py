from __future__ import annotations

import argparse

from gpu_clock.app import run_app
from gpu_clock.figlet import FONT_PRESETS
from gpu_clock.theme import THEME_PRESETS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nvclocktop",
        description="Fullscreen terminal clock and GPU dashboard.",
    )
    parser.add_argument("--refresh", type=float, default=1.0, help="Refresh interval in seconds.")
    parser.add_argument(
        "--font",
        choices=FONT_PRESETS,
        default="terrace",
        help="Clock FIGlet font preset.",
    )
    parser.add_argument(
        "--theme",
        choices=THEME_PRESETS,
        default="rainbow",
        help="Clock color theme preset.",
    )
    parser.add_argument("--clock", choices=["12h", "24h"], default="12h", help="Clock format.")
    seconds = parser.add_mutually_exclusive_group()
    seconds.add_argument(
        "--show-seconds",
        dest="show_seconds",
        action="store_true",
        default=True,
        help="Show seconds in the clock.",
    )
    seconds.add_argument(
        "--hide-seconds",
        dest="show_seconds",
        action="store_false",
        help="Hide seconds in the clock.",
    )
    parser.add_argument("--no-cpu", action="store_true", help="Hide the CPU panel.")
    parser.add_argument("--no-processes", action="store_true", help="Hide the GPU process table.")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render one snapshot and exit. Useful during early development and tests.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_app(args)
