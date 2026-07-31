#!/usr/bin/env python3
"""Refresh a released vocabulary after a bounded, reviewed FST relation change."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from build_tokenizer_vocabulary import ordered_tokens, sha256_file
from tamil_morph_tokenizer.fallback import build_tamil_grapheme_inventory
from tamil_morph_tokenizer.fst import DEFAULT_FST_DIR, DEFAULT_MODEL_ORDER
from tamil_morph_tokenizer.signature import DEFAULT_CODEBOOK_PATH, TagSignatureCodebook


DEFAULT_VOCABULARY_DIR = (
    Path(__file__).resolve().parents[1]
    / "tamil_morph_tokenizer"
    / "data"
    / "vocabulary"
)
PATH_COUNT_RE = re.compile(r"([0-9]+) paths\.")


def upper_path_count(path: Path, foma_bin: str) -> int:
    completed = subprocess.run(
        [
            foma_bin,
            "-q",
            "-e",
            f"load stack {path}",
            "-e",
            "print size",
            "-e",
            "quit",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    match = PATH_COUNT_RE.search(completed.stdout)
    if match is None:
        raise RuntimeError(f"Could not parse Foma path count for {path.name}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lemma", action="append", default=[])
    parser.add_argument("--fst-dir", type=Path, default=DEFAULT_FST_DIR)
    parser.add_argument("--vocabulary-dir", type=Path, default=DEFAULT_VOCABULARY_DIR)
    parser.add_argument("--foma-bin", default="foma")
    args = parser.parse_args()

    token_path = args.vocabulary_dir / "tokens.txt"
    manifest_path = args.vocabulary_dir / "manifest.json"
    old_tokens = tuple(token_path.read_text(encoding="utf-8").splitlines())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    old_graphemes: tuple[str, ...] = ()
    old_grapheme_artifact = manifest.get("tamil_graphemes")
    if old_grapheme_artifact:
        old_graphemes = tuple(
            (args.vocabulary_dir / old_grapheme_artifact["path"])
            .read_text(encoding="utf-8")
            .splitlines()
        )
    elif (
        (args.vocabulary_dir / "tamil_graphemes.txt").is_file()
        and any(token.startswith("<TAMIL_GRAPHEME_") for token in old_tokens)
    ):
        old_graphemes = tuple(
            (args.vocabulary_dir / "tamil_graphemes.txt")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    infrastructure_count = len(ordered_tokens(set(), set(), old_graphemes))
    semantic_count = int(manifest["counts"]["semantic_tokens"])
    semantic_tokens = set(
        old_tokens[infrastructure_count : infrastructure_count + semantic_count]
    )
    lemmas = set(old_tokens[infrastructure_count + semantic_count :])
    reviewed = set(args.lemma)
    added_lemmas = reviewed - lemmas
    lemmas.update(reviewed)
    added_lemma_count = len(lemmas) - int(manifest["counts"]["lemmas"])

    tamil_graphemes = build_tamil_grapheme_inventory(lemmas)
    tokens = ordered_tokens(lemmas, semantic_tokens, tamil_graphemes)
    token_path.write_text("\n".join(tokens) + "\n", encoding="utf-8")
    grapheme_path = args.vocabulary_dir / "tamil_graphemes.txt"
    grapheme_path.write_text(
        "\n".join(tamil_graphemes) + "\n",
        encoding="utf-8",
    )

    manifest["schema_version"] = "0.4.0"
    manifest["ordering"] = [
        "reserved",
        "structural",
        "fst_models",
        "compound_links",
        "compound_variants",
        "tag_variants",
        "realization",
        "utf8_bytes",
        "tamil_graphemes",
        "semantic_sorted",
        "fst_lemmas_sorted",
    ]
    manifest["counts"]["tokens"] = len(tokens)
    manifest["counts"]["lemmas"] = len(lemmas)
    manifest["counts"]["fst_emitted_lexical_strings"] += added_lemma_count
    manifest["counts"]["tamil_grapheme_tokens"] = len(tamil_graphemes)
    manifest["vocabulary_sha256"] = sha256_file(token_path)
    manifest["tamil_graphemes"] = {
        "path": grapheme_path.name,
        "sha256": sha256_file(grapheme_path),
    }
    manifest["fst_artifacts"] = {
        model: {
            "sha256": sha256_file(args.fst_dir / model),
            "upper_analysis_count": upper_path_count(
                args.fst_dir / model,
                args.foma_bin,
            ),
        }
        for model in DEFAULT_MODEL_ORDER
    }
    manifest["tag_signature_codebook"] = {
        "sha256": sha256_file(DEFAULT_CODEBOOK_PATH),
        "entries": len(TagSignatureCodebook()),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "added_lemmas": sorted(added_lemmas),
                "tamil_graphemes": len(tamil_graphemes),
                "tokens": len(tokens),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
