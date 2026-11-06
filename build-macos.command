#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
echo 'KADOMA — native macOS build'
echo 'Use native Python 3.11–3.13 for this Mac. The other architecture needs its own native build.'
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-desktop.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build.py
echo 'App and DMG created in dist/ and release/. These are not Developer ID-signed or notarized.'
