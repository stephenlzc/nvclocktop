from __future__ import annotations

from functools import lru_cache

import pyfiglet


FONT_PRESETS = ("terrace", "big", "standard", "slant", "chunky")


def render_time(value: str, font: str = "terrace") -> str:
    normalized = _normalize_font(font)
    try:
        return _fixed_width_figlet(value, normalized)
    except pyfiglet.FontNotFound:
        return _fixed_width_figlet(value, "big")


def _fixed_width_figlet(value: str, font: str) -> str:
    rendered_chars = [_render_char(char, font) for char in value]
    height = max((len(lines) for lines in rendered_chars), default=0)
    output_lines = []

    for line_index in range(height):
        parts = []
        for char, lines in zip(value, rendered_chars):
            cell_width = _cell_width(char, font)
            line = lines[line_index] if line_index < len(lines) else ""
            parts.append(line.ljust(cell_width))
        output_lines.append("".join(parts).rstrip())

    return "\n".join(output_lines)


@lru_cache(maxsize=None)
def _render_char(char: str, font: str) -> tuple[str, ...]:
    lines = [line.rstrip() for line in pyfiglet.figlet_format(char, font=font, width=200).splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return tuple(lines)


@lru_cache(maxsize=None)
def _cell_width(char: str, font: str) -> int:
    if char.isdigit():
        return _max_char_width("0123456789", font)
    if char in ":":
        return _max_char_width(":", font)
    if char == " ":
        return _max_char_width(" ", font)
    if char.upper() in "APM":
        return _max_char_width("APM", font)
    return max((len(line) for line in _render_char(char, font)), default=1)


@lru_cache(maxsize=None)
def _max_char_width(chars: str, font: str) -> int:
    return max(max((len(line) for line in _render_char(char, font)), default=1) for char in chars)


def _normalize_font(font: str) -> str:
    if font.lower() == "terrace":
        return "ansi_shadow"
    return font
