from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .fst import PACKAGE_DIR


DEFAULT_DECOMPOSITION_PATH = (
    PACKAGE_DIR / "data" / "vocabulary" / "productive_compound_decompositions.tsv"
)
LINK_TOKEN_MAP = {
    "vpart": "<LINK_VPART>",
    "inf": "<LINK_INFINITIVE>",
    "light": "<COMPOUND_LIGHT_VERB>",
    "intensifier": "<INTENSIFIER>",
}


@dataclass(frozen=True)
class CompoundLink:
    form: str
    lemma: str

    @property
    def token(self) -> str:
        try:
            return LINK_TOKEN_MAP[self.form]
        except KeyError as exc:
            raise ValueError(f"Unsupported compound link form: {self.form!r}") from exc


@dataclass(frozen=True)
class CompoundDecomposition:
    compound_lemma: str
    base_lemma: str
    links: tuple[CompoundLink, ...]

    def tokens_for_morphology(self, morph_tokens: tuple[str, ...] = ()) -> tuple[str, ...]:
        tokens: list[str] = [self.base_lemma]
        for link in self.links:
            if link.lemma == "படு":
                if "<VOICE_PASSIVE>" not in morph_tokens:
                    tokens.append("<VOICE_PASSIVE>")
                continue
            tokens.extend((link.token, link.lemma))
        return tuple(tokens)

    @property
    def semantic_tokens(self) -> tuple[str, ...]:
        return self.tokens_for_morphology()


class ProductiveCompoundLexicon:
    """Lazy reviewed decomposition map for FST-only productive compounds."""

    def __init__(self, path: str | Path = DEFAULT_DECOMPOSITION_PATH) -> None:
        self.path = Path(path)
        self._entries: dict[str, CompoundDecomposition] | None = None
        self._reverse: dict[
            bool,
            dict[tuple[str, ...], tuple[str, ...]],
        ] = {}

    def _load(self) -> dict[str, CompoundDecomposition]:
        if self._entries is None:
            manifest_path = self.path.with_suffix(".manifest.json")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
            if digest != manifest.get("sha256"):
                raise ValueError("Productive compound map checksum does not match manifest")
            entries: dict[str, CompoundDecomposition] = {}
            lines = self.path.read_text(encoding="utf-8").splitlines()
            for line in lines[1:]:
                compound, base, typed_chain = line.split("\t")
                links = tuple(
                    CompoundLink(*item.split(":", 1))
                    for item in typed_chain.split("|")
                )
                entries[compound] = CompoundDecomposition(
                    compound_lemma=compound,
                    base_lemma=base,
                    links=links,
                )
            if len(entries) != manifest.get("entries"):
                raise ValueError("Productive compound map count does not match manifest")
            self._entries = entries
        return self._entries

    def get(self, lemma: str) -> CompoundDecomposition | None:
        return self._load().get(lemma)

    def is_light_compound(self, lemma: str) -> bool:
        decomposition = self.get(lemma)
        return bool(
            decomposition
            and any(link.form == "light" for link in decomposition.links)
        )

    def entries(self) -> dict[str, CompoundDecomposition]:
        return dict(self._load())

    def compound_lemmas(
        self,
        lexical_tokens: tuple[str, ...],
        morph_tokens: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        passive_context = "<VOICE_PASSIVE>" in morph_tokens
        if passive_context not in self._reverse:
            grouped: dict[tuple[str, ...], list[str]] = {}
            for lemma, decomposition in self._load().items():
                tokens = decomposition.tokens_for_morphology(morph_tokens)
                grouped.setdefault(tokens, []).append(lemma)
            self._reverse[passive_context] = {
                tokens: tuple(sorted(lemmas))
                for tokens, lemmas in grouped.items()
            }
        return self._reverse[passive_context].get(lexical_tokens, ())

    def match_compound_tokens(
        self,
        tokens: tuple[str, ...],
        morph_tokens: tuple[str, ...] = (),
    ) -> tuple[tuple[str, ...], int]:
        max_length = min(5, len(tokens))
        for length in range(max_length, 1, -1):
            candidates = self.compound_lemmas(tokens[:length], morph_tokens)
            if candidates:
                return candidates, length
        return (), 0

    def __len__(self) -> int:
        return len(self._load())

    def semantic_tokens(
        self,
        lemma: str,
        morph_tokens: tuple[str, ...] = (),
        *,
        productive_reading: bool = True,
    ) -> tuple[str, ...]:
        if not productive_reading:
            return (lemma,)
        decomposition = self.get(lemma)
        return decomposition.tokens_for_morphology(morph_tokens) if decomposition else (lemma,)
