# Release Notes

## v1.0.0

Initial stable release of `nvclocktop`, a fullscreen terminal clock and GPU dashboard for NVIDIA Linux workstations and Apple Silicon Macs.

### Highlights

- Large fullscreen terminal clock with selectable FIGlet-style font presets.
- Color theme presets for terminal dashboards, including rainbow, cyber, ocean, amber, and mono.
- NVIDIA GPU monitoring through `nvidia-smi`, including utilization, memory, temperature, power, fan, driver, and process information.
- Apple Silicon GPU summary with Metal support and unified memory display.
- CPU panel with usage, memory, load average, frequency, temperature, and per-thread activity.
- Adaptive layout for compact and wide terminals.
- Keyboard controls for quitting and toggling help.
- One-shot render mode for screenshots, testing, and documentation assets.

### Installation

```bash
pip install nvclocktop
```

### Usage

```bash
nvclocktop
```

Useful options:

```bash
nvclocktop --theme cyber
nvclocktop --font big
nvclocktop --refresh 1
nvclocktop --once
```

### Supported Platforms

- Linux with NVIDIA GPUs and `nvidia-smi`
- macOS on Apple Silicon
- CPU-only display on other supported Python environments

### Notes

- The package name and command are both `nvclocktop`.
- This release is published as version `1.0.0`.
