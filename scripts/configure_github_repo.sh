#!/usr/bin/env bash
set -euo pipefail

description="A fullscreen terminal clock and GPU dashboard for NVIDIA Linux workstations and Apple Silicon Macs."
topics="gpu,nvidia,nvidia-smi,terminal,tui,dashboard,monitoring,clock,python,rich,macos,apple-silicon,linux,ai-workstation,homelab"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required to configure the repository." >&2
  exit 1
fi

gh repo edit --description "$description" --add-topic "$topics"
echo "GitHub repository description and topics have been configured."
