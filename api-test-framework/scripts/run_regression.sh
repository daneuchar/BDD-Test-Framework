#!/usr/bin/env bash
# Run regression tests only in parallel with Allure reporting.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

pytest -n auto -m regression --alluredir=reports/allure-results "$@"
