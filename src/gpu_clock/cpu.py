from __future__ import annotations

from dataclasses import dataclass
import os
import platform
import subprocess

import psutil


@dataclass(frozen=True)
class CpuInfo:
    model: str
    usage_percent: float
    per_cpu_percent: list[float]
    memory_used_gib: float
    memory_total_gib: float
    load_average: tuple[float, float, float] | None
    thread_count: int
    frequency_ghz: float | None
    temperature_c: float | None


def collect_cpu_info() -> CpuInfo:
    memory = psutil.virtual_memory()
    frequency = psutil.cpu_freq()
    return CpuInfo(
        model=_cpu_model(),
        usage_percent=psutil.cpu_percent(interval=None),
        per_cpu_percent=psutil.cpu_percent(interval=None, percpu=True),
        memory_used_gib=(memory.total - memory.available) / 1024**3,
        memory_total_gib=memory.total / 1024**3,
        load_average=_load_average(),
        thread_count=psutil.cpu_count(logical=True) or 0,
        frequency_ghz=(frequency.current / 1000) if frequency else None,
        temperature_c=_cpu_temperature(),
    )


def _cpu_model() -> str:
    if platform.system() == "Darwin":
        return _mac_cpu_model()
    if platform.system() != "Linux":
        return platform.processor() or platform.machine() or "Unknown CPU"
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
            for line in cpuinfo:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "Unknown CPU"


def _mac_cpu_model() -> str:
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        )
    except (OSError, subprocess.SubprocessError, TimeoutError):
        result = None
    if result and result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return platform.processor() or platform.machine() or "Apple Silicon"


def _load_average() -> tuple[float, float, float] | None:
    try:
        return os.getloadavg()
    except OSError:
        return None


def _cpu_temperature() -> float | None:
    try:
        temperatures = psutil.sensors_temperatures()
    except (AttributeError, OSError):
        return None
    for entries in temperatures.values():
        for entry in entries:
            label = (entry.label or "").lower()
            if "cpu" in label or "package" in label or "core" in label:
                return float(entry.current)
    for entries in temperatures.values():
        if entries:
            return float(entries[0].current)
    return None
