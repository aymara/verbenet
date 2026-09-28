#!/usr/bin/env python3
"""bumpver pre-commit hook: turn the "Unreleased" section of CHANGELOG.md into the new version."""
import os
import subprocess
from pathlib import Path

version = os.environ["BUMPVER_NEW_VERSION"]
changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
text = changelog.read_text(encoding="utf-8")
if "## Unreleased\n" not in text:
    raise SystemExit("CHANGELOG.md has no '## Unreleased' section")
changelog.write_text(text.replace("## Unreleased\n", f"## Unreleased\n\n## {version}\n", 1), encoding="utf-8")
subprocess.run(["git", "add", str(changelog)], check=True)
