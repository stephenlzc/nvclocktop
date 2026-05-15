#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f PyPi_token ]]; then
  echo "PyPi_token not found in the current directory." >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required to set the repository secret." >&2
  exit 1
fi

token="$(grep -m 1 '^pypi-' PyPi_token | tr -d '[:space:]')"
if [[ -z "$token" ]]; then
  echo "PyPi_token does not contain a token line beginning with pypi-." >&2
  exit 1
fi

printf '%s' "$token" | gh secret set PYPI_API_TOKEN
echo "GitHub secret PYPI_API_TOKEN has been set from PyPi_token."
