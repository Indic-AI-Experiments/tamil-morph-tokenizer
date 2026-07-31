from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_package_api_and_release_versions_match() -> None:
    release = json.loads(
        (ROOT / "tokenizer.release.json").read_text(encoding="utf-8")
    )["release"]["version"]
    project = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    api_source = (
        ROOT / "tamil_morph_tokenizer" / "api.py"
    ).read_text(encoding="utf-8")
    api_match = re.search(r'(?m)^\s*version="([^"]+)",$', api_source)

    assert api_match is not None
    assert project == release.replace("-", "")
    assert api_match.group(1) == release
