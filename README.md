<div align="center">

<h1>nvclocktop</h1>

<p>
  <strong>A fullscreen terminal clock and GPU dashboard for NVIDIA Linux workstations and Apple Silicon Macs.</strong>
</p>

<p>
  Turn any terminal into a live status screen for AI workstations, local model machines, homelab servers, and SSH sessions.
</p>

<img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/hero-macos-apple-silicon.png" alt="nvclocktop running on an Apple Silicon Mac">

</div>

---

`nvclocktop` combines a large readable clock, CPU activity, memory usage, and GPU metrics in one colorful terminal dashboard.

## Preset Gallery

<table>
  <tr>
    <th><code>--font terrace --theme rainbow</code></th>
    <th><code>--font terrace --theme cyber</code></th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/presets/preset-terrace-rainbow-nvidia.png" alt="terrace font with rainbow theme on NVIDIA Linux" width="420"></td>
    <td><img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/presets/preset-terrace-cyber-nvidia.png" alt="terrace font with cyber theme on NVIDIA Linux" width="420"></td>
  </tr>
  <tr>
    <th><code>--font big --theme ocean</code></th>
    <th><code>--font standard --theme amber</code></th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/presets/preset-big-ocean-nvidia.png" alt="big font with ocean theme on NVIDIA Linux" width="420"></td>
    <td><img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/presets/preset-standard-amber-nvidia.png" alt="standard font with amber theme on NVIDIA Linux" width="420"></td>
  </tr>
  <tr>
    <th><code>--font slant --theme mono</code></th>
    <th></th>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/stephenlzc/nvclocktop/main/docs/assets/presets/preset-slant-mono-nvidia.png" alt="slant font with mono theme on NVIDIA Linux" width="420"></td>
    <td></td>
  </tr>
</table>

## Installation

```bash
pip install nvclocktop
```

Or with `pipx`:

```bash
pipx install nvclocktop
```

## Usage

```bash
nvclocktop
```

Useful options:

```bash
nvclocktop --refresh 1
nvclocktop --once
nvclocktop --font big
nvclocktop --theme cyber
```

## Features

- Large fixed-position terminal clock with seconds
- CPU usage, memory, load average, and per-thread activity
- NVIDIA GPU usage, memory, temperature, power, fan, and driver info on Linux
- Apple Silicon GPU and unified memory display on macOS
- Adaptive layout for wide and compact terminals
- Keyboard controls: `Q` to quit, `H` for help
- Works well over SSH

## Style Presets

`nvclocktop` ships with official clock font and color presets. Invalid preset names are rejected by the CLI, so saved scripts and dashboard setups fail fast instead of silently falling back to an unexpected style.

Available font presets:

```bash
nvclocktop --font terrace
nvclocktop --font big
nvclocktop --font standard
nvclocktop --font slant
nvclocktop --font chunky
```

Available color themes:

```bash
nvclocktop --theme rainbow
nvclocktop --theme cyber
nvclocktop --theme ocean
nvclocktop --theme amber
nvclocktop --theme mono
```

## Platform Support

Currently supported:

| Platform | GPU support | Notes |
| --- | --- | --- |
| Linux | NVIDIA GPUs via `nvidia-smi` | Best supported path |
| macOS | Apple Silicon GPU display | Includes unified memory display |
| CPU | Intel and AMD CPUs | Uses standard system metrics |

Not currently supported:

- AMD GPUs
- Intel GPUs
- Windows native terminal

## Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `Q` | Quit |
| `H` | Show or hide help |
| `Ctrl+C` | Quit immediately |

## Development

```bash
git clone https://github.com/stephenlzc/nvclocktop.git
cd nvclocktop
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

MIT
