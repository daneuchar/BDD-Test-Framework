#!/usr/bin/env bash
# Generate and serve the Allure report.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RESULTS_DIR="$PROJECT_DIR/reports/allure-results"

if [ ! -d "$RESULTS_DIR" ]; then
    echo "Error: No allure results found at $RESULTS_DIR"
    echo "Run tests first: ./scripts/run_tests.sh"
    exit 1
fi

allure serve "$RESULTS_DIR"
