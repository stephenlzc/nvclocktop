from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops
from rich.console import Console
from rich.console import Group
from rich.text import Text

from gpu_clock.cpu import CpuInfo
from gpu_clock.cpu import collect_cpu_info
from gpu_clock.figlet import FONT_PRESETS
from gpu_clock.figlet import render_time
from gpu_clock.gpu import GpuInfo, GpuSummary
from gpu_clock.gpu import collect_gpu_info
from gpu_clock.layout import build_snapshot
from gpu_clock.theme import THEME_PRESETS, clock_text


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "assets"
PRESET_DIR = ASSET_DIR / "presets"
PRESET_IMAGE_SIZE = (1400, 470)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render README PNG assets.")
    parser.add_argument(
        "--live-output",
        type=Path,
        help="Render one PNG from live system metrics instead of regenerating README assets.",
    )
    args = parser.parse_args()
    if args.live_output:
        _render_live(args.live_output)
        return

    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    _render("hero-linux-nvidia", font="terrace", theme="rainbow", width=151, height=32)
    _render("macos-apple-silicon", font="terrace", theme="cyber", width=151, height=32, apple=True)
    _render("compact-layout", font="standard", theme="mono", width=87, height=24, apple=True)

    for font in FONT_PRESETS:
        _render_preset(f"presets/font-{font}", font=font, theme="rainbow")

    for theme in THEME_PRESETS:
        _render_preset(f"presets/theme-{theme}", font="terrace", theme=theme)


def _render_live(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _render_snapshot(
        path,
        args=argparse.Namespace(
            clock="12h",
            font="terrace",
            no_cpu=False,
            no_processes=True,
            once=True,
            refresh=1.0,
            show_seconds=True,
            theme="rainbow",
        ),
        cpu_info=collect_cpu_info(),
        gpu_info=collect_gpu_info(include_processes=False),
        width=151,
        height=32,
        title="nvclocktop live",
    )


def _render(
    name: str,
    *,
    font: str,
    theme: str,
    width: int,
    height: int,
    apple: bool = False,
) -> None:
    args = argparse.Namespace(
        clock="12h",
        font=font,
        no_cpu=False,
        no_processes=True,
        once=True,
        refresh=1.0,
        show_seconds=True,
        theme=theme,
    )
    _render_snapshot(
        png_path=ASSET_DIR / f"{name}.png",
        args=args,
        cpu_info=_cpu_info(apple),
        gpu_info=_gpu_info(apple),
        width=width,
        height=height,
        title=f"nvclocktop {name}",
    )


def _render_snapshot(
    png_path: Path,
    *,
    args: argparse.Namespace,
    cpu_info: CpuInfo,
    gpu_info: GpuInfo,
    width: int,
    height: int,
    title: str,
) -> None:
    console = Console(
        record=True,
        file=StringIO(),
        width=width,
        height=height,
        force_terminal=True,
        color_system="truecolor",
    )
    console.print(
        build_snapshot(
            args=args,
            cpu_info=cpu_info,
            gpu_info=gpu_info,
            terminal_width=width,
            terminal_height=height,
        )
    )
    svg_path = png_path.with_suffix(".svg")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(console.export_svg(title=title), encoding="utf-8")
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=1600)
    _crop_vertical_white_margin(png_path)
    svg_path.unlink(missing_ok=True)


def _render_preset(name: str, *, font: str, theme: str) -> None:
    console = Console(
        record=True,
        file=StringIO(),
        width=104,
        height=16,
        force_terminal=True,
        color_system="truecolor",
    )
    art = render_time("12:56:23 AM", font=font)
    console.print(
        Group(
            Text(f"--font {font}  --theme {theme}", justify="center", style="bold"),
            Text(""),
            clock_text(art, theme),
        )
    )
    svg_path = ASSET_DIR / f"{name}.svg"
    png_path = ASSET_DIR / f"{name}.png"
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(console.export_svg(title=f"nvclocktop {name}"), encoding="utf-8")
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=PRESET_IMAGE_SIZE[0])
    _crop_to_fixed_canvas(png_path, PRESET_IMAGE_SIZE)
    svg_path.unlink(missing_ok=True)


def _cpu_info(apple: bool) -> CpuInfo:
    return CpuInfo(
        model="Apple M1 Pro" if apple else "Intel i7-12700K",
        usage_percent=33 if apple else 18,
        per_cpu_percent=[12, 31, 48, 7, 65, 22, 9, 41, 18, 3],
        memory_used_gib=12.9 if apple else 9.7,
        memory_total_gib=16.0 if apple else 62.6,
        load_average=(5.53, 5.08, 5.53) if apple else (0.42, 0.24, 0.18),
        thread_count=10 if apple else 20,
        frequency_ghz=3.23 if apple else 4.9,
        temperature_c=None if apple else 43,
    )


def _gpu_info(apple: bool) -> GpuInfo:
    if apple:
        gpu = GpuSummary(
            name="Apple M1 Pro",
            utilization_percent=None,
            memory_used_mib=13247,
            memory_total_mib=16384,
            temperature_c=None,
            power_draw_w=None,
            power_limit_w=None,
            fan_percent=None,
            driver_version="Metal 3",
            backend="Apple",
            core_count=16,
            memory_label="Unified Memory",
        )
    else:
        gpu = GpuSummary(
            name="NVIDIA GeForce RTX 4060 Ti",
            utilization_percent=42,
            memory_used_mib=3920,
            memory_total_mib=16380,
            temperature_c=47,
            power_draw_w=74.6,
            power_limit_w=165,
            fan_percent=31,
            driver_version="550.107.02",
        )
    return GpuInfo(available=True, error=None, gpus=[gpu], processes=[])


def _crop_vertical_white_margin(path: Path) -> None:
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    diff = ImageChops.difference(image, background).convert("L")
    bbox = diff.point(lambda value: 255 if value > 8 else 0).getbbox()
    if bbox is None:
        return
    padding = 10
    top = max(bbox[1] - padding, 0)
    bottom = min(bbox[3] + padding, image.height)
    image.crop((0, top, image.width, bottom)).save(path)


def _crop_to_fixed_canvas(path: Path, size: tuple[int, int]) -> None:
    image = Image.open(path).convert("RGBA")
    cropped = _cropped_white_margin(image, padding=8)
    canvas = Image.new("RGBA", size, (38, 38, 38, 255))
    if cropped.width > size[0] or cropped.height > size[1]:
        cropped.thumbnail((size[0], size[1]), Image.Resampling.LANCZOS)
    left = (size[0] - cropped.width) // 2
    top = (size[1] - cropped.height) // 2
    canvas.alpha_composite(cropped, (left, top))
    canvas.save(path)


def _cropped_white_margin(image: Image.Image, padding: int) -> Image.Image:
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    diff = ImageChops.difference(image, background).convert("L")
    bbox = diff.point(lambda value: 255 if value > 8 else 0).getbbox()
    if bbox is None:
        return image
    left = max(bbox[0] - padding, 0)
    top = max(bbox[1] - padding, 0)
    right = min(bbox[2] + padding, image.width)
    bottom = min(bbox[3] + padding, image.height)
    return image.crop((left, top, right, bottom))


if __name__ == "__main__":
    main()
