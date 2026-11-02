import pytest

from gpu_clock.figlet import FONT_PRESETS, render_time_cells
from gpu_clock.theme import THEME_PRESETS, clock_text, rainbow_text


def test_rainbow_text_keeps_content():
    rendered = rainbow_text("12:34")
    assert rendered.plain.strip() == "12:34"


def test_clock_text_supports_all_theme_presets():
    for theme in THEME_PRESETS:
        rendered = clock_text("12:34", theme)
        assert rendered.plain.strip() == "12:34"


@pytest.mark.parametrize("font", FONT_PRESETS)
@pytest.mark.parametrize("value", ["10:44:34 AM", "10:44 PM", "23:59:59", "09:07"])
def test_rainbow_uses_one_color_per_figlet_character(font, value):
    art, widths = render_time_cells(value, font)
    rendered = clock_text(art, "rainbow", widths)
    assert rendered.plain == art + "\n"
    styles = [None] * len(rendered.plain)
    for span in rendered.spans:
        styles[span.start:span.end] = [span.style] * (span.end - span.start)

    character_styles = [set() for _ in value]
    offset = 0
    for line in art.splitlines():
        column = 0
        for index, width in enumerate(widths):
            for position in range(column, min(column + width, len(line))):
                if not line[position].isspace():
                    character_styles[index].add(styles[offset + position])
            column += width
        offset += len(line) + 1

    for char, colors in zip(value, character_styles):
        if char != " ":
            assert len(colors) == 1
            assert None not in colors
    assert len(set.union(*character_styles)) >= 4
