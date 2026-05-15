from gpu_clock.cli import build_parser
from gpu_clock.figlet import FONT_PRESETS
from gpu_clock.theme import THEME_PRESETS


def test_cli_accepts_official_font_and_theme_presets():
    parser = build_parser()

    for font in FONT_PRESETS:
        args = parser.parse_args(["--font", font, "--once"])
        assert args.font == font

    for theme in THEME_PRESETS:
        args = parser.parse_args(["--theme", theme, "--once"])
        assert args.theme == theme


def test_cli_rejects_unknown_font_or_theme():
    parser = build_parser()

    for option in ("--font", "--theme"):
        try:
            parser.parse_args([option, "unknown-preset"])
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError(f"{option} accepted an unknown preset")
