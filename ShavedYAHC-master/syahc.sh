#!/bin/bash

set -euo pipefail

if [ ! -d venv ]; then
  echo "(Setting up Python environment...)"
  (
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -e .
  ) || (rm -rf venv; rm -rf *.egg-info; exit 1)
  echo
fi

source venv/bin/activate
syahc "$@"
