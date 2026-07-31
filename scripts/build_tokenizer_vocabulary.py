#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import unicodedata

from tamil_morph_tokenizer.fallback import (
    build_tamil_grapheme_inventory,
    tamil_grapheme_token,
)
from tamil_morph_tokenizer.analysis import parse_analysis
from tamil_morph_tokenizer.auxiliary_inventory import (
    INVENTORY_FILENAME,
    load_auxiliary_inventory,
)
from tamil_morph_tokenizer.codec import (
    FST_LEMMA_BYTES_END,
    FST_LEMMA_BYTES_START,
    LEXICAL_BYTES_END,
    LEXICAL_BYTES_START,
    COMPOUND_VARIANT_TOKENS,
    MODEL_TO_TOKEN,
    SURFACE_BYTES,
    WORD_START,
)
from tamil_morph_tokenizer.decomposition import LINK_TOKEN_MAP, ProductiveCompoundLexicon
from tamil_morph_tokenizer.fst import DEFAULT_FST_DIR, DEFAULT_MODEL_ORDER
from tamil_morph_tokenizer.entity import (
    DEFAULT_ENTITY_GAZETTEER_PATH,
    ENTITY_TOKENS,
)
from tamil_morph_tokenizer.realization import REALIZATION_TOKENS
from tamil_morph_tokenizer.signature import (
    DEFAULT_CODEBOOK_PATH,
    TAG_VARIANT_TOKENS,
    TagSignatureCodebook,
)
from tamil_morph_tokenizer.tokenizer import (
    ALT_TOKEN,
    READINGS_TOKEN,
    SPECIAL_TOKENS,
    is_tamil_word,
)


RESERVED_TOKENS = ("<PAD>", "<BOS>", "<EOS>", "<UNK>")
STRUCTURAL_TOKENS = (
    WORD_START,
    SURFACE_BYTES,
    FST_LEMMA_BYTES_START,
    FST_LEMMA_BYTES_END,
    LEXICAL_BYTES_START,
    LEXICAL_BYTES_END,
    READINGS_TOKEN,
    ALT_TOKEN,
)
BYTE_TOKENS = tuple(f"<BYTE_{value:02X}>" for value in range(256))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def enumerate_upper_analyses(fst_path: Path, foma_bin: str):
    process = subprocess.Popen(
        [
            foma_bin,
            "-q",
            "-e",
            f"load stack {fst_path}",
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
        raise RuntimeError("Failed to capture foma output")
    for line in process.stdout:
        raw = line.strip()
        if raw:
            yield raw
    stderr = process.stderr.read() if process.stderr is not None else ""
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"foma failed for {fst_path.name}: {stderr.strip()}")


def collect_runtime_vocabulary(fst_dir: Path, foma_bin: str):
    lemmas: set[str] = set()
    semantic_tokens: set[str] = set(SPECIAL_TOKENS.values())
    model_counts: dict[str, int] = {}

    for model_name in DEFAULT_MODEL_ORDER:
        fst_path = fst_dir / model_name
        if not fst_path.exists():
            continue
        analysis_count = 0
        if model_name == "verb-auxiliary.fst":
            inventory_path = fst_dir / INVENTORY_FILENAME
            if not inventory_path.exists():
                raise RuntimeError(
                    f"{inventory_path} is required for compact composition inventory"
                )
            auxiliary_lemmas, auxiliary_frequencies, analysis_count = (
                load_auxiliary_inventory(inventory_path)
            )
            lemmas.update(auxiliary_lemmas)
            raw_analyses = (
                f"__AUXILIARY__+{raw_tags}"
                for raw_tags in auxiliary_frequencies
            )
        else:
            raw_analyses = enumerate_upper_analyses(fst_path, foma_bin)
        for raw in raw_analyses:
            analysis = parse_analysis(raw, model=model_name)
            if not analysis.is_recognized:
                continue
            if model_name != "verb-auxiliary.fst":
                analysis_count += 1
                lemmas.add(analysis.lemma)
            semantic_tokens.update(analysis.morph_tokens)
        model_counts[model_name] = analysis_count

    return lemmas, semantic_tokens, model_counts


def ordered_tokens(
    lemmas: set[str],
    semantic_tokens: set[str],
    tamil_graphemes: tuple[str, ...],
) -> tuple[str, ...]:
    groups = (
        RESERVED_TOKENS,
        STRUCTURAL_TOKENS,
        tuple(MODEL_TO_TOKEN.values()),
        tuple(LINK_TOKEN_MAP.values()),
        COMPOUND_VARIANT_TOKENS,
        TAG_VARIANT_TOKENS,
        REALIZATION_TOKENS,
        BYTE_TOKENS,
        tuple(tamil_grapheme_token(grapheme) for grapheme in tamil_graphemes),
        tuple(sorted(semantic_tokens)),
        tuple(sorted(lemmas)),
    )
    tokens: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for token in group:
            if token not in seen:
                seen.add(token)
                tokens.append(token)
    return tuple(tokens)


def validate_lemmas(lemmas: set[str]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for lemma in sorted(lemmas):
        categories: list[str] = []
        details: list[str] = []
        if lemma != unicodedata.normalize("NFC", lemma):
            categories.append("non_nfc")
        for char in lemma:
            category = unicodedata.category(char)
            if category in {"Cc", "Cf", "Cs"}:
                categories.append("control_or_format")
                details.append(f"U+{ord(char):04X}")
                continue
            if char == "-":
                continue
            if 0x0B80 <= ord(char) <= 0x0BFF or category.startswith("M"):
                continue
            categories.append("unexpected_character")
            details.append(f"{char}=U+{ord(char):04X}")
        if "-" in lemma and not is_tamil_word(lemma):
            categories.append("splitter_unreachable_hyphen")
        if categories:
            issues.append(
                {
                    "lemma": lemma,
                    "categories": "|".join(dict.fromkeys(categories)),
                    "details": "|".join(dict.fromkeys(details)),
                }
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the fixed tokenizer vocabulary from runtime FST upper languages."
    )
    parser.add_argument("--fst-dir", type=Path, default=DEFAULT_FST_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tamil_morph_tokenizer/data/vocabulary"),
    )
    parser.add_argument("--foma-bin", default="foma")
    parser.add_argument(
        "--allow-validation-errors",
        action="store_true",
        help="Write a provisional audit artifact even when corrupt lemmas are emitted.",
    )
    args = parser.parse_args()

    if shutil.which(args.foma_bin) is None:
        raise SystemExit(f"{args.foma_bin!r} not found. Install foma first.")

    lemmas, semantic_tokens, model_counts = collect_runtime_vocabulary(
        args.fst_dir, args.foma_bin
    )
    fst_emitted_lemmas = set(lemmas)
    semantic_tokens.update(ENTITY_TOKENS)
    emitted_lexical_count = len(lemmas)
    all_compound_entries = ProductiveCompoundLexicon().entries()
    stale_decomposition_entries = set(all_compound_entries) - lemmas
    compound_entries = {
        lemma: decomposition
        for lemma, decomposition in all_compound_entries.items()
        if lemma in lemmas
    }
    decomposed_compounds = set(compound_entries)
    excluded_compounds = lemmas & decomposed_compounds
    lemmas.difference_update(excluded_compounds)
    lemmas.update(
        token
        for decomposition in compound_entries.values()
        for token in decomposition.semantic_tokens
        if not token.startswith("<")
    )
    decomposition_only_lemmas = lemmas - fst_emitted_lemmas
    tamil_graphemes = build_tamil_grapheme_inventory(lemmas)
    tokens = ordered_tokens(lemmas, semantic_tokens, tamil_graphemes)
    validation_issues = validate_lemmas(lemmas)
    blocking_issues = [
        issue
        for issue in validation_issues
        if any(
            category in issue["categories"].split("|")
            for category in ("non_nfc", "control_or_format", "unexpected_character")
        )
    ]
    splitter_issues = [
        issue
        for issue in validation_issues
        if "splitter_unreachable_hyphen" in issue["categories"].split("|")
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    token_path = args.output_dir / "tokens.txt"
    token_path.write_text("\n".join(tokens) + "\n", encoding="utf-8")
    tamil_grapheme_path = args.output_dir / "tamil_graphemes.txt"
    tamil_grapheme_path.write_text(
        "\n".join(tamil_graphemes) + "\n",
        encoding="utf-8",
    )

    fst_artifacts = {
        model: {
            "sha256": sha256_file(args.fst_dir / model),
            "upper_analysis_count": model_counts[model],
        }
        for model in DEFAULT_MODEL_ORDER
        if model in model_counts
    }
    manifest = {
        "schema_version": "0.3.0",
        "ordering": [
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
        ],
        "counts": {
            "tokens": len(tokens),
            "lemmas": len(lemmas),
            "fst_emitted_lexical_strings": emitted_lexical_count,
            "decomposition_only_lexical_strings": len(decomposition_only_lemmas),
            "excluded_productive_compounds": len(excluded_compounds),
            "stale_decomposition_entries_ignored": len(stale_decomposition_entries),
            "semantic_tokens": len(semantic_tokens),
            "byte_tokens": len(BYTE_TOKENS),
            "tamil_grapheme_tokens": len(tamil_graphemes),
            "blocking_lemma_issues": len(blocking_issues),
            "splitter_unreachable_lemmas": len(splitter_issues),
        },
        "release_ready": not blocking_issues and not splitter_issues,
        "vocabulary_sha256": sha256_file(token_path),
        "tamil_graphemes": {
            "path": tamil_grapheme_path.name,
            "sha256": sha256_file(tamil_grapheme_path),
        },
        "fst_artifacts": fst_artifacts,
        "tag_signature_codebook": {
            "sha256": sha256_file(DEFAULT_CODEBOOK_PATH),
            "entries": len(TagSignatureCodebook()),
        },
        "decomposition_only_lexical_strings": sorted(decomposition_only_lemmas),
        "entity_gazetteer": {
            "sha256": sha256_file(DEFAULT_ENTITY_GAZETTEER_PATH),
            "manifest_sha256": sha256_file(
                DEFAULT_ENTITY_GAZETTEER_PATH.with_suffix(".manifest.json")
            ),
        },
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    issue_path = args.output_dir / "validation_issues.csv"
    with issue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("lemma", "categories", "details"))
        writer.writeheader()
        writer.writerows(validation_issues)
    print(json.dumps(manifest["counts"], sort_keys=True))
    if (blocking_issues or splitter_issues) and not args.allow_validation_errors:
        print(
            "Refusing release-ready vocabulary: "
            f"{len(blocking_issues)} corrupt lemma entries and "
            f"{len(splitter_issues)} splitter-unreachable entries. "
            "See validation_issues.csv."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
