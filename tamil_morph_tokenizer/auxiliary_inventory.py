from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


INVENTORY_FILENAME = "verb-auxiliary.inventory.json"


def load_auxiliary_inventory(path: Path) -> tuple[set[str], Counter[str], int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "0.1.0":
        raise ValueError("Unsupported auxiliary upper-inventory schema")
    lemmas = set(payload["lemmas"])
    frequencies = Counter(
        {str(tags): int(count) for tags, count in payload["raw_tag_frequencies"]}
    )
    upper_count = sum(frequencies.values())
    if upper_count != int(payload["upper_analysis_count"]):
        raise ValueError("Auxiliary upper-inventory count does not match entries")
    return lemmas, frequencies, upper_count
