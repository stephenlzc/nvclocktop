from gpu_clock.theme import THEME_PRESETS, clock_text, rainbow_text


def test_rainbow_text_keeps_content():
    rendered = rainbow_text("12:34")
    assert rendered.plain.strip() == "12:34"


def test_clock_text_supports_all_theme_presets():
    for theme in THEME_PRESETS:
        rendered = clock_text("12:34", theme)
        assert rendered.plain.strip() == "12:34"
