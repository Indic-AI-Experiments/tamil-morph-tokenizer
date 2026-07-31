#!/usr/bin/env python3
"""Merge bounded FST relation files into the exact tag-signature codebook."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from tamil_morph_tokenizer.analysis import parse_analysis
from tamil_morph_tokenizer.fst import DEFAULT_FST_DIR, DEFAULT_MODEL_ORDER
from tamil_morph_tokenizer.signature import DEFAULT_CODEBOOK_PATH


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--relation",
        action="append",
        default=[],
        metavar="MODEL=TSV",
        help="FST model name and two-column analysis/surface TSV to merge",
    )
    parser.add_argument(
        "--replace-model",
        action="append",
        default=[],
        metavar="MODEL",
        help="Replace one model's codebook rows from its complete upper language",
    )
    parser.add_argument("--fst-dir", type=Path, default=DEFAULT_FST_DIR)
    parser.add_argument("--codebook", type=Path, default=DEFAULT_CODEBOOK_PATH)
    parser.add_argument("--foma-bin", default="foma")
    args = parser.parse_args()
    if not args.relation and not args.replace_model:
        parser.error("at least one --relation or --replace-model is required")

    grouped: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)
    with args.codebook.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            grouped[
                (row["model"], tuple(json.loads(row["semantic_tokens_json"])))
            ].add(row["raw_tags"])

    def add_raw(model: str, raw: str) -> int:
        analysis = parse_analysis(raw, model=model)
        if not analysis.is_recognized:
            raise SystemExit(f"Unrecognized {model} analysis: {raw!r}")
        _, separator, raw_tags = raw.partition("+")
        raw_tags = raw_tags if separator else ""
        key = (model, analysis.morph_tokens)
        before = len(grouped[key])
        grouped[key].add(raw_tags)
        return len(grouped[key]) - before

    replaced = 0
    for model in args.replace_model:
        if model not in DEFAULT_MODEL_ORDER:
            raise SystemExit(f"Invalid replacement model: {model!r}")
        model_path = args.fst_dir / model
        if not model_path.is_file():
            raise SystemExit(f"Missing replacement FST: {model_path}")
        stale_keys = [key for key in grouped if key[0] == model]
        for key in stale_keys:
            replaced += len(grouped.pop(key))
        process = subprocess.Popen(
            [
                args.foma_bin,
                "-q",
                "-e",
                f"load stack {model_path}",
                "-e",
                "print upper-words 2147483647",
                "-e",
                "quit",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.stdout is None:
            raise RuntimeError(f"Failed to enumerate {model}")
        for line in process.stdout:
            raw = line.strip()
            if raw:
                add_raw(model, raw)
        stderr = process.stderr.read() if process.stderr is not None else ""
        if process.wait() != 0:
            raise RuntimeError(f"foma failed for {model}: {stderr.strip()}")

    added = 0
    for specification in args.relation:
        model, separator, path_text = specification.partition("=")
        if not separator or model not in DEFAULT_MODEL_ORDER:
            raise SystemExit(f"Invalid relation specification: {specification!r}")
        path = Path(path_text)
        with path.open(encoding="utf-8", newline="") as handle:
            for line_number, row in enumerate(csv.reader(handle, delimiter="\t"), 1):
                if not row or (row[0].lstrip().startswith("#")):
                    continue
                if len(row) != 2:
                    raise SystemExit(f"{path}:{line_number}: expected two TSV fields")
                try:
                    added += add_raw(model, row[0])
                except SystemExit as error:
                    raise SystemExit(f"{path}:{line_number}: {error}") from error

    with args.codebook.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(("model", "semantic_tokens_json", "variant", "raw_tags"))
        for (model, semantic_tokens), raw_values in sorted(grouped.items()):
            encoded = json.dumps(
                semantic_tokens,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            for variant, raw_tags in enumerate(sorted(raw_values)):
                writer.writerow((model, encoded, variant, raw_tags))

    manifest = {
        "schema_version": "0.1.0",
        "entries": sum(len(values) for values in grouped.values()),
        "keys": len(grouped),
        "maximum_variants_per_key": max(map(len, grouped.values())),
        "sha256": sha256(args.codebook),
        "fst_artifacts": {
            model: sha256(args.fst_dir / model)
            for model in DEFAULT_MODEL_ORDER
            if (args.fst_dir / model).is_file()
        },
    }
    args.codebook.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"replaced {replaced} old model patterns; "
        f"merged {added} new raw-tag patterns; "
        f"{manifest['entries']} entries across {manifest['keys']} keys"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
