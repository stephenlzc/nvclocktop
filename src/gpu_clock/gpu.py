from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import os
import platform
from pathlib import Path
import pwd
import shutil
import subprocess

import psutil


@dataclass(frozen=True)
class GpuSummary:
    name: str
    utilization_percent: float | None
    memory_used_mib: float | None
    memory_total_mib: float | None
    temperature_c: float | None
    power_draw_w: float | None
    power_limit_w: float | None
    fan_percent: float | None
    driver_version: str | None
    backend: str = "NVIDIA"
    core_count: int | None = None
    memory_label: str = "Memory"


@dataclass(frozen=True)
class GpuProcess:
    pid: int
    process_name: str
    used_memory_mib: float | None
    user: str | None = None
    command: str | None = None


@dataclass(frozen=True)
class GpuInfo:
    available: bool
    error: str | None
    gpus: list[GpuSummary]
    processes: list[GpuProcess]


def collect_gpu_info(include_processes: bool = True) -> GpuInfo:
    if platform.system() == "Darwin":
        return collect_apple_gpu_info()

    if shutil.which("nvidia-smi") is None:
        return GpuInfo(
            available=False,
            error="nvidia-smi not found. NVIDIA GPU support requires NVIDIA drivers.",
            gpus=[],
            processes=[],
        )

    try:
        gpus = query_gpu_summary()
        processes = query_gpu_processes() if include_processes else []
    except subprocess.SubprocessError as exc:
        return GpuInfo(available=False, error=str(exc), gpus=[], processes=[])

    return GpuInfo(available=True, error=None, gpus=gpus, processes=processes)


def collect_apple_gpu_info() -> GpuInfo:
    try:
        gpus = query_apple_gpu_summary()
    except subprocess.SubprocessError as exc:
        return GpuInfo(available=False, error=str(exc), gpus=[], processes=[])
    return GpuInfo(available=bool(gpus), error=None if gpus else "Apple GPU not detected.", gpus=gpus, processes=[])


def query_apple_gpu_summary() -> list[GpuSummary]:
    output = subprocess.run(
        ["system_profiler", "SPDisplaysDataType", "-json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if output.returncode != 0:
        raise subprocess.CalledProcessError(
            output.returncode,
            output.args,
            output.stdout,
            output.stderr,
        )

    memory = psutil.virtual_memory()
    entries = json.loads(output.stdout).get("SPDisplaysDataType", [])
    summaries = []
    for entry in entries:
        name = entry.get("sppci_model") or entry.get("_name") or "Apple GPU"
        cores = _int_text(entry.get("sppci_cores"))
        metal = _metal_version(entry.get("spdisplays_mtlgpufamilysupport"))
        summaries.append(
            GpuSummary(
                name=name,
                utilization_percent=None,
                memory_used_mib=(memory.total - memory.available) / 1024**2,
                memory_total_mib=memory.total / 1024**2,
                temperature_c=None,
                power_draw_w=None,
                power_limit_w=None,
                fan_percent=None,
                driver_version=metal,
                backend="Apple",
                core_count=cores,
                memory_label="Unified Memory",
            )
        )
    return summaries


def query_gpu_summary() -> list[GpuSummary]:
    output = _run_nvidia_smi(
        [
            "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,"
            "power.draw,power.limit,fan.speed,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    rows = _parse_csv_lines(output)
    return [_gpu_summary_from_row(row) for row in rows if row]


def query_gpu_processes() -> list[GpuProcess]:
    output = _run_nvidia_smi(
        [
            "--query-compute-apps=pid,process_name,used_memory",
            "--format=csv,noheader,nounits",
        ],
        allow_empty=True,
    )
    rows = _parse_csv_lines(output)
    return [_gpu_process_from_row(row) for row in rows if len(row) >= 3]


def _run_nvidia_smi(args: list[str], allow_empty: bool = False) -> str:
    result = subprocess.run(
        ["nvidia-smi", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=3,
    )
    if result.returncode != 0 and not allow_empty:
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
    if result.returncode != 0 and allow_empty:
        return ""
    return result.stdout.strip()


def _parse_csv_lines(output: str) -> list[list[str]]:
    if not output:
        return []
    return [[cell.strip() for cell in row] for row in csv.reader(output.splitlines())]


def _gpu_summary_from_row(row: list[str]) -> GpuSummary:
    return GpuSummary(
        name=_text(row, 0, "Unknown NVIDIA GPU"),
        utilization_percent=_number(row, 1),
        memory_used_mib=_number(row, 2),
        memory_total_mib=_number(row, 3),
        temperature_c=_number(row, 4),
        power_draw_w=_number(row, 5),
        power_limit_w=_number(row, 6),
        fan_percent=_number(row, 7),
        driver_version=_optional_text(row, 8),
    )


def _gpu_process_from_row(row: list[str]) -> GpuProcess:
    pid = int(_number(row, 0) or 0)
    return GpuProcess(
        pid=pid,
        process_name=_text(row, 1, "unknown"),
        used_memory_mib=_number(row, 2),
        user=_process_user(pid),
        command=_process_command(pid),
    )


def _process_user(pid: int) -> str | None:
    try:
        stat_info = os.stat(f"/proc/{pid}")
    except OSError:
        return None
    try:
        return pwd.getpwuid(stat_info.st_uid).pw_name
    except KeyError:
        return str(stat_info.st_uid)


def _process_command(pid: int) -> str | None:
    proc_path = Path(f"/proc/{pid}")
    try:
        command = proc_path.joinpath("cmdline").read_text(encoding="utf-8", errors="replace")
    except OSError:
        command = ""
    command = " ".join(part for part in command.split("\0") if part).strip()
    if command:
        return command

    try:
        return proc_path.joinpath("comm").read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None


def _number(row: list[str], index: int) -> float | None:
    if index >= len(row):
        return None
    value = row[index].strip()
    if not value or value.upper() == "N/A":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _text(row: list[str], index: int, fallback: str) -> str:
    value = _optional_text(row, index)
    return value or fallback


def _optional_text(row: list[str], index: int) -> str | None:
    if index >= len(row):
        return None
    value = row[index].strip()
    if not value or value.upper() == "N/A":
        return None
    return value


def _int_text(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _metal_version(value: object) -> str | None:
    text = str(value or "").lower()
    if "metal3" in text:
        return "Metal 3"
    if "metal2" in text:
        return "Metal 2"
    if "metal" in text:
        return "Metal"
    return None
