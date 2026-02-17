#!/usr/bin/env bash
# Run the full test suite in parallel with Allure reporting.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

pytest -n auto --alluredir=reports/allure-results "$@"
