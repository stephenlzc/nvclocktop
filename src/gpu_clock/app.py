from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
import select
import sys
import termios
import time
import tty
from typing import TextIO

from rich.align import Align
from rich.console import Console
from rich.live import Live

from gpu_clock.cpu import collect_cpu_info
from gpu_clock.gpu import collect_gpu_info
from gpu_clock.layout import build_snapshot


QUIT_KEY = "quit"
HELP_KEY = "help"


def run_app(args: argparse.Namespace) -> int:
    console = Console()
    if args.once:
        console.print(_build_current_snapshot(args, console=console))
        return 0

    refresh = _refresh_interval(args.refresh)
    show_help = False
    try:
        with _terminal_cbreak(sys.stdin):
            with Live(
                _build_live_snapshot(args, console, show_help=show_help),
                console=console,
                refresh_per_second=max(1, int(1 / refresh)),
                screen=True,
                transient=False,
            ) as live:
                while True:
                    tick_started = time.monotonic()
                    live.update(_build_live_snapshot(args, console, show_help=show_help), refresh=True)
                    action = _wait_for_next_tick_or_key(sys.stdin, tick_started, refresh)
                    if action == QUIT_KEY:
                        return 0
                    if action == HELP_KEY:
                        show_help = not show_help
    except KeyboardInterrupt:
        return 0


def _build_current_snapshot(
    args: argparse.Namespace,
    console: Console | None = None,
    show_help: bool = False,
):
    cpu_info = None if args.no_cpu else collect_cpu_info()
    gpu_info = collect_gpu_info(include_processes=False)
    terminal_width = console.size.width if console else None
    terminal_height = console.size.height if console else None
    return build_snapshot(
        args=args,
        cpu_info=cpu_info,
        gpu_info=gpu_info,
        show_help=show_help,
        terminal_width=terminal_width,
        terminal_height=terminal_height,
    )


def _build_live_snapshot(args: argparse.Namespace, console: Console, show_help: bool = False):
    return Align.center(
        _build_current_snapshot(args, console=console, show_help=show_help),
        vertical="middle",
        height=console.size.height,
        width=console.size.width,
    )


def _refresh_interval(value: float) -> float:
    if value <= 0:
        return 1.0
    return max(0.1, value)


def _wait_for_next_tick_or_key(stdin: TextIO, tick_started: float, refresh: float) -> str | None:
    while True:
        action = _read_action(stdin)
        if action is not None:
            return action
        remaining = refresh - (time.monotonic() - tick_started)
        if remaining <= 0:
            return None
        time.sleep(min(remaining, 0.05))


def _read_action(stdin: TextIO) -> str | None:
    if not stdin.isatty():
        return None
    readable, _, _ = select.select([stdin], [], [], 0)
    if not readable:
        return None
    return _key_action(stdin.read(1))


def _key_action(key: str) -> str | None:
    normalized = key.lower()
    if normalized == "q":
        return QUIT_KEY
    if normalized == "h":
        return HELP_KEY
    return None


@contextmanager
def _terminal_cbreak(stdin: TextIO):
    if not stdin.isatty():
        with nullcontext():
            yield
        return

    file_descriptor = stdin.fileno()
    previous_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setcbreak(file_descriptor)
        yield
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, previous_settings)
