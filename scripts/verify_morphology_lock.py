#!/usr/bin/env python3
"""Verify an installed Tamil morphology runtime against its release lock."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(lock_path: Path, runtime_dir: Path) -> list[str]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = [
        *lock["runtime"]["artifacts"],
        *lock["runtime"].get("sidecars", []),
    ]
    errors: list[str] = []
    expected_names = {str(row["file"]) for row in expected}
    actual_names = {
        path.name
        for path in runtime_dir.iterdir()
        if path.is_file() and path.suffix in {".fst", ".json"}
    }
    for name in sorted(expected_names - actual_names):
        errors.append(f"missing artifact: {name}")
    for name in sorted(actual_names - expected_names):
        errors.append(f"unexpected artifact: {name}")
    for row in expected:
        path = runtime_dir / str(row["file"])
        if not path.exists():
            continue
        actual_size = path.stat().st_size
        if actual_size != int(row["size_bytes"]):
            errors.append(
                f"size mismatch for {path.name}: {actual_size} != {row['size_bytes']}"
            )
        actual_hash = sha256(path)
        if actual_hash != row["sha256"]:
            errors.append(
                f"sha256 mismatch for {path.name}: {actual_hash} != {row['sha256']}"
            )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lock",
        type=Path,
        default=ROOT / "morphology.lock.json",
    )
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=ROOT / "tamil_morph_tokenizer" / "data" / "fst-models",
    )
    args = parser.parse_args()
    errors = verify(args.lock.resolve(), args.runtime_dir.resolve())
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"verified {args.runtime_dir} against {args.lock}")


if __name__ == "__main__":
    main()
