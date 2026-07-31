#!/usr/bin/env python3
"""Refresh tokenizer and morphology release metadata from installed artifacts."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from tamil_morph_tokenizer.fst import DEFAULT_MODEL_ORDER


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, object]:
    return {
        "file": path.name,
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sync_package_versions(tokenizer_version: str) -> None:
    pep440_version = tokenizer_version.replace("-", "")
    pyproject_path = ROOT / "pyproject.toml"
    pyproject = pyproject_path.read_text(encoding="utf-8")
    updated_pyproject, pyproject_replacements = re.subn(
        r'(?m)^(version = ")[^"]+(")$',
        rf"\g<1>{pep440_version}\g<2>",
        pyproject,
        count=1,
    )
    if pyproject_replacements != 1:
        raise ValueError("Could not update the project version in pyproject.toml")
    pyproject_path.write_text(updated_pyproject, encoding="utf-8")

    api_path = ROOT / "tamil_morph_tokenizer" / "api.py"
    api = api_path.read_text(encoding="utf-8")
    updated_api, api_replacements = re.subn(
        r'(?m)^(\s*version=")[^"]+(",)$',
        rf"\g<1>{tokenizer_version}\g<2>",
        api,
        count=1,
    )
    if api_replacements != 1:
        raise ValueError("Could not update the FastAPI version")
    api_path.write_text(updated_api, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--morphology-version", required=True)
    parser.add_argument("--tokenizer-version", required=True)
    parser.add_argument("--source-state", required=True)
    parser.add_argument("--source-build-manifest", type=Path, required=True)
    parser.add_argument("--explicit-noun-roots", type=int, required=True)
    parser.add_argument("--runtime-recognized-lemmas", type=int, required=True)
    parser.add_argument("--compact-symbolic-upper-analyses", type=int, required=True)
    parser.add_argument("--enumerated-relation-paths", type=int, required=True)
    args = parser.parse_args()

    lock_path = ROOT / "morphology.lock.json"
    release_path = ROOT / "tokenizer.release.json"
    fst_dir = ROOT / "tamil_morph_tokenizer" / "data" / "fst-models"
    vocabulary_dir = ROOT / "tamil_morph_tokenizer" / "data" / "vocabulary"
    vocabulary_manifest_path = vocabulary_dir / "manifest.json"
    codebook_manifest_path = vocabulary_dir / "tag_signature_codebook.manifest.json"

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    vocabulary = json.loads(vocabulary_manifest_path.read_text(encoding="utf-8"))
    codebook = json.loads(codebook_manifest_path.read_text(encoding="utf-8"))
    source_build = json.loads(args.source_build_manifest.read_text(encoding="utf-8"))

    lock["release"]["version"] = args.morphology_version
    release_date = date.today().isoformat()
    lock["release"]["date"] = release_date
    lock["provenance"]["source_state"] = args.source_state
    lock["inventory"]["compact_symbolic_upper_analyses"] = (
        args.compact_symbolic_upper_analyses
    )
    lock["inventory"]["enumerated_relation_paths"] = args.enumerated_relation_paths
    lock["inventory"]["exact_tag_signature_patterns"] = codebook["entries"]
    lock["inventory"]["explicit_unique_noun_roots"] = args.explicit_noun_roots
    lock["inventory"]["fixed_vocabulary_lemmas"] = vocabulary["counts"]["lemmas"]
    lock["inventory"]["fixed_vocabulary_tokens"] = vocabulary["counts"]["tokens"]
    lock["inventory"]["manifest_patch_records"] = len(source_build["patches"])
    lock["inventory"]["manifest_unique_patch_files"] = len(
        {row["file"] for row in source_build["patches"]}
    )
    lock["inventory"]["runtime_recognized_lemmas"] = args.runtime_recognized_lemmas
    lock["inventory"]["unique_semantic_signature_keys"] = codebook["keys"]
    lock["relation"]["compact_symbolic_upper_analyses"] = (
        args.compact_symbolic_upper_analyses
    )
    lock["relation"]["enumerated_relation_paths"] = args.enumerated_relation_paths
    lock["relation"]["exact_tag_patterns"] = codebook["entries"]
    lock["relation"]["semantic_signature_keys"] = codebook["keys"]
    lock["runtime"]["artifacts"] = [
        artifact(fst_dir / model) for model in DEFAULT_MODEL_ORDER
    ]
    lock["runtime"]["sidecars"] = [
        artifact(fst_dir / "verb-auxiliary.inventory.json")
    ]
    lock["validation"]["exact_signature_roundtrip_failures"] = 0
    lock["validation"]["exact_signature_roundtrips"] = codebook["entries"]
    lock["validation"]["source_build_manifest_sha256"] = sha256(
        args.source_build_manifest
    )
    write_json(lock_path, lock)

    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["release"]["version"] = args.tokenizer_version
    release["release"]["date"] = release_date
    release["morphology"]["version"] = args.morphology_version
    release["validation"]["exact_signature_roundtrip_failures"] = 0
    release["validation"]["exact_signature_roundtrips"] = codebook["entries"]
    release["validation"]["exact_tag_patterns"] = codebook["entries"]
    release["vocabulary"]["schema_version"] = vocabulary["schema_version"]
    release["vocabulary"]["sha256"] = vocabulary["vocabulary_sha256"]
    release["vocabulary"]["counts"] = vocabulary["counts"]
    release["vocabulary"]["artifacts"] = [
        artifact(path)
        for path in sorted(vocabulary_dir.iterdir())
        if path.is_file()
    ]
    write_json(release_path, release)
    sync_package_versions(args.tokenizer_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
