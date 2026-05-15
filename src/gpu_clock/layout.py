from __future__ import annotations

import argparse
from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from gpu_clock.cpu import CpuInfo
from gpu_clock.figlet import render_time
from gpu_clock.gpu import GpuInfo
from gpu_clock.theme import clock_text


PANEL_HEIGHT = 14
COMPACT_PANEL_HEIGHT = 9


def build_snapshot(
    args: argparse.Namespace,
    cpu_info: CpuInfo | None,
    gpu_info: GpuInfo,
    show_help: bool = False,
    terminal_width: int | None = None,
    terminal_height: int | None = None,
) -> Group:
    compact = _compact_layout(terminal_width, terminal_height)
    now = datetime.now()
    time_value = _format_time(now, args.clock, args.show_seconds)
    date_line = now.strftime("%B %-d, %Y | %A")

    time_art = render_time(time_value, font=_time_font(args.font, compact))
    header_width = terminal_width or 120
    header = Group(
        Align.center(clock_text(time_art, args.theme), width=header_width),
        Align.center(Text(date_line, style="bold"), width=header_width),
        Align.center(Text("Q Quit | H Help", style="dim"), width=header_width),
    )

    if show_help:
        return Group(header, Text(""), _help_panel(compact))

    bottom = Table.grid(expand=True)
    if cpu_info is not None:
        bottom.add_column(ratio=1)
    bottom.add_column(ratio=2)

    row = []
    if cpu_info is not None:
        row.append(_cpu_panel(cpu_info, compact))
    row.append(_gpu_panel(gpu_info, compact, terminal_width))
    bottom.add_row(*row)

    return Group(header, Text(""), bottom)


def _compact_layout(width: int | None, height: int | None) -> bool:
    return (width is not None and width < 100) or (height is not None and height < 28)


def _time_font(font: str, compact: bool) -> str:
    if compact and font == "terrace":
        return "standard"
    return font


def _panel_height(compact: bool) -> int:
    return COMPACT_PANEL_HEIGHT if compact else PANEL_HEIGHT


def _help_panel(compact: bool) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()
    table.add_row("Q", "Quit nvclocktop and restore the terminal.")
    table.add_row("H", "Show or hide this help screen.")
    table.add_row("Ctrl+C", "Quit immediately.")
    return Panel(
        Align.center(table, vertical="middle"),
        title="Help",
        box=box.SQUARE,
        height=_panel_height(compact),
    )


def _format_time(now: datetime, clock: str, show_seconds: bool) -> str:
    if clock == "24h":
        return now.strftime("%H:%M:%S" if show_seconds else "%H:%M")
    return now.strftime("%I:%M:%S %p" if show_seconds else "%I:%M %p")


def _cpu_panel(cpu: CpuInfo, compact: bool = False) -> Panel:
    table = Table.grid(expand=True)
    table.add_column(width=7)
    table.add_column(ratio=2)
    bar_width = 8 if compact else 18
    table.add_row(Text("CPU", style="bold dim"), Text(_short_cpu_model(cpu.model), style="bold"))
    table.add_row(Text("Use", style="bold dim"), _status_bar(cpu.usage_percent, bar_width, "green", value_suffix="%"))
    if compact:
        table.add_row(
            Text("RAM", style="bold dim"),
            Text(f"{cpu.memory_used_gib:.1f}/{cpu.memory_total_gib:.1f} GiB", style="bold cyan"),
        )
    else:
        table.add_row(
            Text("RAM", style="bold dim"),
            _status_bar(
                _memory_percent(cpu.memory_used_gib, cpu.memory_total_gib),
                bar_width,
                "cyan",
                value_text=f"{cpu.memory_used_gib:.1f}/{cpu.memory_total_gib:.1f} GiB",
            ),
        )
    if cpu.load_average:
        table.add_row(Text("Load", style="bold dim"), Text(_load_text(cpu, compact), style="white"))
    if not compact:
        table.add_row(Text("Freq", style="bold dim"), Text(_frequency_text(cpu), style="white"))
        table.add_row(Text("Temp", style="bold dim"), Text(_temperature_text(cpu), style="yellow"))
    table.add_row(Text("Threads", style="bold dim"), _thread_grid(cpu.per_cpu_percent))
    return Panel(table, title="CPU", box=box.SQUARE, height=_panel_height(compact))


def _gpu_panel(gpu_info: GpuInfo, compact: bool = False, terminal_width: int | None = None) -> Panel:
    if not gpu_info.available:
        return Panel(
            gpu_info.error or "NVIDIA GPU not detected.",
            title="GPU",
            box=box.SQUARE,
            height=_panel_height(compact),
        )

    summary = Table.grid(expand=True)
    summary.add_column(width=10)
    summary.add_column(ratio=1)
    summary.add_column(width=22)
    bar_width = _gpu_bar_width(terminal_width, compact)

    for index, gpu in enumerate(gpu_info.gpus):
        summary.add_row(
            Text("Device", style="bold dim"),
            _gpu_title(index, gpu.name),
            Text(""),
        )
        if gpu.core_count:
            summary.add_row(
                Text("Cores", style="bold dim"),
                Text(f"{gpu.core_count} GPU cores", style="bold white"),
                Text(""),
            )
        summary.add_row(
            Text("GPU", style="bold dim"),
            _metric_bar(gpu.utilization_percent, bar_width, "green"),
            _metric_value(gpu.utilization_percent, "green", suffix="%"),
        )
        summary.add_row(
            Text(_fit_label(gpu.memory_label), style="bold dim"),
            _metric_bar(
                _memory_percent(gpu.memory_used_mib, gpu.memory_total_mib),
                bar_width,
                "cyan",
            ),
            _metric_value_text(_memory(gpu.memory_used_mib, gpu.memory_total_mib, compact), "cyan"),
        )
        if not compact or gpu.temperature_c is not None:
            summary.add_row(
                Text("Temp", style="bold dim"),
                _metric_bar(_temperature_percent(gpu.temperature_c), bar_width, "yellow"),
                _metric_value_text(_fmt(gpu.temperature_c, " C"), "yellow"),
            )
        if not compact or gpu.power_draw_w is not None:
            summary.add_row(
                Text("Power", style="bold dim"),
                _metric_bar(_memory_percent(gpu.power_draw_w, gpu.power_limit_w), bar_width, "magenta"),
                _metric_value_text(_power(gpu.power_draw_w, gpu.power_limit_w), "magenta"),
            )
        if not compact or gpu.fan_percent is not None:
            summary.add_row(
                Text("Fan", style="bold dim"),
                _metric_bar(gpu.fan_percent, bar_width, "blue"),
                _metric_value(gpu.fan_percent, "blue", suffix="%"),
            )
        summary.add_row(
            Text(_gpu_driver_label(gpu.backend), style="bold dim"),
            Text(gpu.driver_version or "N/A", style="dim"),
            Text(""),
        )

    return Panel(summary, title="GPU", box=box.SQUARE, height=_panel_height(compact))


def _gpu_title(index: int, name: str) -> Text:
    text = Text()
    text.append(f"GPU {index}", style="bold cyan")
    text.append(f"  {name}", style="bold")
    return text


def _fit_label(label: str) -> str:
    if label == "Unified Memory":
        return "Unified"
    return label


def _gpu_driver_label(backend: str) -> str:
    if backend == "Apple":
        return "Metal"
    return "Driver"


def _gpu_bar_width(terminal_width: int | None, compact: bool) -> int:
    if compact:
        return 18
    if terminal_width is None:
        return 36
    return max(24, min(96, int(terminal_width * 0.35)))


def _metric_bar(percent: float | None, width: int, style: str) -> Text:
    text = Text(no_wrap=True, overflow="crop")
    if percent is None:
        text.append(" " * width, style="on #3a3a3a")
        return text

    clamped = max(0, min(percent, 100))
    filled = round(clamped / 100 * width)
    text.append(" " * filled, style=f"on {style}")
    text.append(" " * (width - filled), style="on #3a3a3a")
    return text


def _metric_value(value: float | None, style: str, suffix: str = "") -> Text:
    if value is None:
        return Text("N/A", style="dim", no_wrap=True)
    return Text(f"{max(0, min(value, 100)):.0f}{suffix}", style=f"bold {style}", no_wrap=True)


def _metric_value_text(value: str, style: str) -> Text:
    if value == "N/A":
        return Text(value, style="dim", no_wrap=True)
    return Text(value, style=f"bold {style}", no_wrap=True)


def _status_bar(
    percent: float | None,
    width: int,
    style: str,
    value_text: str | None = None,
    value_suffix: str = "",
) -> Text:
    text = Text(no_wrap=True, overflow="ellipsis")
    if percent is None:
        text.append(" " * width, style="on #3a3a3a")
        text.append("  N/A", style="dim")
        return text

    clamped = max(0, min(percent, 100))
    filled = round(clamped / 100 * width)
    text.append(" " * filled, style=f"on {style}")
    text.append(" " * (width - filled), style="on #3a3a3a")
    label = value_text if value_text is not None else f"{clamped:.0f}{value_suffix}"
    text.append(f"  {label}", style=f"bold {style}")
    return text


def _thread_grid(values: list[float]) -> Text:
    text = Text()
    for index, value in enumerate(values):
        if index and index % 10 == 0:
            text.append("\n")
        text.append("■", style=_usage_style(value))
        if index % 10 != 9:
            text.append(" ")
    if not values:
        text.append("N/A", style="dim")
    return text


def _short_cpu_model(model: str) -> str:
    return (
        model.replace("12th Gen Intel(R) Core(TM)", "Intel")
        .replace("Intel(R) Core(TM)", "Intel")
        .replace("AMD Ryzen", "Ryzen")
    )


def _usage_style(value: float) -> str:
    if value >= 85:
        return "bold red"
    if value >= 60:
        return "bold yellow"
    if value >= 30:
        return "bold green"
    return "dim"


def _load_text(cpu: CpuInfo, compact: bool = False) -> str:
    if compact:
        return " ".join(f"{value:.1f}" for value in cpu.load_average or ())
    return " / ".join(f"{value:.2f}" for value in cpu.load_average or ())


def _frequency_text(cpu: CpuInfo) -> str:
    frequency = f"{cpu.frequency_ghz:.2f} GHz" if cpu.frequency_ghz else "N/A"
    return f"{cpu.thread_count} threads   {frequency}"


def _temperature_text(cpu: CpuInfo) -> str:
    return f"{cpu.temperature_c:.0f} C" if cpu.temperature_c else "N/A"


def _fmt(value: float | None, suffix: str) -> str:
    if value is None:
        return "N/A"
    return f"{value:.0f}{suffix}"


def _memory(used: float | None, total: float | None, compact: bool = False) -> str:
    if used is None or total is None:
        return "N/A"
    if compact:
        return f"{used / 1024:.1f}/{total / 1024:.1f} GiB"
    return f"{used:.0f} / {total:.0f} MiB"


def _memory_percent(used: float | None, total: float | None) -> float | None:
    if used is None or total in (None, 0):
        return None
    return used / total * 100


def _temperature_percent(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 90 * 100


def _power(draw: float | None, limit: float | None) -> str:
    if draw is None:
        return "N/A"
    if limit is None:
        return f"{draw:.1f} W"
    return f"{draw:.1f} / {limit:.0f} W"
