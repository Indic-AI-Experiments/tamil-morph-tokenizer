from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_semantic_token_reference_is_complete_and_current() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_semantic_token_reference.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    payload = json.loads(
        (
            ROOT
            / "tamil_morph_tokenizer/data/vocabulary/semantic_token_reference.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["count"] == 222
    assert payload["model_factor_region_count"] == 284
    assert payload["secondary_lexical_component_count"] == 62
    assert len(payload["entries"]) == 222
    assert len(payload["secondary_lexical_components"]) == 62
    assert all(entry["token"].startswith("<") for entry in payload["entries"])
    assert all(
        not entry["token"].startswith("<")
        for entry in payload["secondary_lexical_components"]
    )
    assert len({entry["token"] for entry in payload["entries"]}) == 222
    assert all(entry["description"].strip() for entry in payload["entries"])
