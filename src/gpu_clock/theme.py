from __future__ import annotations

from rich.text import Text


CLOCK_THEMES = {
    "rainbow": [
        (231, 72, 86),
        (226, 106, 20),
        (220, 158, 0),
        (98, 168, 0),
        (0, 153, 94),
        (0, 137, 163),
        (37, 91, 201),
        (127, 46, 176),
    ],
    "cyber": [
        (0, 229, 255),
        (0, 184, 255),
        (80, 117, 255),
        (177, 74, 255),
        (255, 67, 210),
    ],
    "ocean": [
        (91, 206, 250),
        (45, 156, 219),
        (33, 150, 136),
        (39, 174, 96),
        (166, 226, 161),
    ],
    "amber": [
        (255, 202, 40),
        (255, 171, 0),
        (255, 112, 67),
        (255, 213, 79),
    ],
    "mono": [
        (245, 245, 245),
        (210, 210, 210),
        (170, 170, 170),
    ],
}

THEME_PRESETS = tuple(CLOCK_THEMES)

RAINBOW_2 = CLOCK_THEMES["rainbow"]


def clock_text(value: str, theme: str = "rainbow") -> Text:
    palette = CLOCK_THEMES[theme]
    return gradient_text(value, palette)


def gradient_text(value: str, palette: list[tuple[int, int, int]]) -> Text:
    text = Text(justify="center")
    for line in value.splitlines():
        width = max(len(line), 1)
        for index, char in enumerate(line):
            color = palette[int(index / width * len(palette))]
            text.append(char, style=f"rgb({color[0]},{color[1]},{color[2]})")
        text.append("\n")
    return text


def rainbow_text(value: str) -> Text:
    return gradient_text(value, RAINBOW_2)
