from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .fst import DEFAULT_FST_DIR, PACKAGE_DIR


DEFAULT_CODEBOOK_PATH = (
    PACKAGE_DIR / "data" / "vocabulary" / "tag_signature_codebook.tsv"
)
TAG_VARIANT_TOKENS = tuple(f"<TAG_VARIANT_{index}>" for index in range(1, 64))


class TagSignatureCodebook:
    """Exact raw FST tag suffixes keyed by model and semantic morphology."""

    def __init__(
        self,
        path: str | Path = DEFAULT_CODEBOOK_PATH,
        fst_dir: str | Path = DEFAULT_FST_DIR,
    ) -> None:
        self.path = Path(path)
        self.fst_dir = Path(fst_dir)
        self._patterns: dict[tuple[str, tuple[str, ...]], tuple[str, ...]] | None = None

    def _load(self) -> dict[tuple[str, tuple[str, ...]], tuple[str, ...]]:
        if self._patterns is not None:
            return self._patterns
        manifest = json.loads(self.path.with_suffix(".manifest.json").read_text())
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        if digest != manifest.get("sha256"):
            raise ValueError("Tag signature codebook checksum does not match manifest")
        for model, expected in manifest.get("fst_artifacts", {}).items():
            actual = hashlib.sha256((self.fst_dir / model).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"Tag signature codebook FST mismatch: {model}")

        grouped: dict[tuple[str, tuple[str, ...]], list[tuple[int, str]]] = {}
        with self.path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                key = (row["model"], tuple(json.loads(row["semantic_tokens_json"])))
                grouped.setdefault(key, []).append((int(row["variant"]), row["raw_tags"]))
        patterns: dict[tuple[str, tuple[str, ...]], tuple[str, ...]] = {}
        for key, values in grouped.items():
            ordered = tuple(raw_tags for _, raw_tags in sorted(values))
            if tuple(range(len(ordered))) != tuple(index for index, _ in sorted(values)):
                raise ValueError(f"Non-contiguous tag signature variants for {key!r}")
            patterns[key] = ordered
        if sum(len(values) for values in patterns.values()) != manifest.get("entries"):
            raise ValueError("Tag signature codebook count does not match manifest")
        self._patterns = patterns
        return patterns

    def patterns(self, model: str, morph_tokens: tuple[str, ...]) -> tuple[str, ...]:
        return self._load().get((model, morph_tokens), ())

    def variant_for(
        self,
        model: str,
        morph_tokens: tuple[str, ...],
        raw_tags: str,
    ) -> int:
        patterns = self.patterns(model, morph_tokens)
        try:
            return patterns.index(raw_tags)
        except ValueError as exc:
            raise ValueError(
                f"Raw tags are absent from signature codebook: {model} {raw_tags!r}"
            ) from exc

    def raw_tags(
        self,
        model: str,
        morph_tokens: tuple[str, ...],
        variant: int,
    ) -> str:
        patterns = self.patterns(model, morph_tokens)
        if not 0 <= variant < len(patterns):
            raise ValueError(
                f"Tag variant {variant} is unavailable for {model} {morph_tokens!r}"
            )
        return patterns[variant]

    def __len__(self) -> int:
        return sum(len(values) for values in self._load().values())
