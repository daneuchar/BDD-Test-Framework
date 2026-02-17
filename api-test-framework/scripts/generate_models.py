#!/usr/bin/env python3
"""Generate Pydantic response models from OpenAPI specs.

Usage:
    python scripts/generate_models.py              # generate for all versions
    python scripts/generate_models.py --version v1 # generate for v1 only
    python scripts/generate_models.py --version v2 # generate for v2 only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OPENAPI_DIR = PROJECT_ROOT / "openapi"
OUTPUT_DIR = PROJECT_ROOT / "models" / "generated"
BASE_CLASS = "models.base_model.BaseDTO"
HEADER = "# AUTO-GENERATED -- DO NOT EDIT\n# Re-generate with: python scripts/generate_models.py\n"

VERSIONS = ["v1", "v2"]


def generate_for_version(version: str) -> None:
    """Run datamodel-code-generator for a single API version."""
    input_path = OPENAPI_DIR / f"{version}.yaml"
    output_path = OUTPUT_DIR / version

    if not input_path.exists():
        print(f"ERROR: OpenAPI spec not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input", str(input_path),
        "--output", str(output_path),
        "--base-class", BASE_CLASS,
        "--snake-case-field",
        "--field-constraints",
        "--target-python-version", "3.11",
        "--output-model-type", "pydantic_v2.BaseModel",
        "--input-file-type", "openapi",
    ]

    print(f"Generating models for {version}...")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR generating {version}:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    # Inject header into each generated .py file
    for py_file in output_path.glob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if not content.startswith("# AUTO-GENERATED"):
            py_file.write_text(HEADER + content, encoding="utf-8")

    print(f"  Done: {version}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Pydantic models from OpenAPI specs.")
    parser.add_argument(
        "--version",
        choices=VERSIONS,
        default=None,
        help="Generate for a specific version only (default: all).",
    )
    args = parser.parse_args()

    versions = [args.version] if args.version else VERSIONS

    for version in versions:
        generate_for_version(version)

    print("\nModel generation complete.")


if __name__ == "__main__":
    main()
