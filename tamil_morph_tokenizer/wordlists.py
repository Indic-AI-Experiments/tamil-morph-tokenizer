from __future__ import annotations

import gzip
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_WORDLIST_DIR = PACKAGE_DIR / "data" / "wordlists"
DEFAULT_VOCABULARY_PATH = PACKAGE_DIR / "data" / "vocabulary" / "tokens.txt"

@dataclass(frozen=True)
class TamilWordLists:
    """Lazy access to packaged Tamil lemma and surface-form inventories."""

    wordlist_dir: Path = DEFAULT_WORDLIST_DIR
    vocabulary_path: Path = DEFAULT_VOCABULARY_PATH

    @cached_property
    def dictionary_path(self) -> Path:
        return self._prefer_plain_or_gzip("tamil_dictionary.txt")

    @cached_property
    def lemma_dictionary_path(self) -> Path:
        return self.wordlist_dir / "lemma_dictionary.txt"

    @cached_property
    def fst_generated_forms_path(self) -> Path:
        return self._prefer_plain_or_gzip("fst_generated_forms.txt")

    @cached_property
    def fst_heuristic_forms_path(self) -> Path:
        return self.wordlist_dir / "fst_heuristic_forms.txt"

    @cached_property
    def dictionary(self) -> tuple[str, ...]:
        return self._load_lines(self.dictionary_path)

    @cached_property
    def lemma_dictionary(self) -> tuple[str, ...]:
        return self._load_lines(self.lemma_dictionary_path)

    @cached_property
    def vocabulary_tokens(self) -> frozenset[str]:
        """Atomic released tokens, used when optional source lists are absent."""
        return frozenset(self._load_lines(self.vocabulary_path))

    @cached_property
    def fst_generated_forms(self) -> frozenset[str]:
        return frozenset(self._load_lines(self.fst_generated_forms_path))

    @cached_property
    def fst_heuristic_forms(self) -> frozenset[str]:
        return frozenset(self._load_lines(self.fst_heuristic_forms_path))

    def contains_dictionary_word(self, word: str) -> bool:
        """Binary search the sorted full surface dictionary."""
        return self._contains_sorted(self.dictionary, word)

    def contains_lemma(self, word: str) -> bool:
        """Check an optional source list, then the always-packaged vocabulary."""
        return (
            self._contains_sorted(self.lemma_dictionary, word)
            or word in self.vocabulary_tokens
        )

    def _contains_sorted(self, words: tuple[str, ...], word: str) -> bool:
        lo = 0
        hi = len(words) - 1
        while lo <= hi:
            mid = (lo + hi) >> 1
            candidate = words[mid]
            if candidate == word:
                return True
            if candidate < word:
                lo = mid + 1
            else:
                hi = mid - 1
        return False

    def source_membership(self, word: str) -> tuple[str, ...]:
        sources: list[str] = []
        if self.contains_dictionary_word(word):
            sources.append("dictionary")
        if self.contains_lemma(word):
            sources.append("lemma_dictionary")
        if word in self.fst_generated_forms:
            sources.append("fst_generated_forms")
        if word in self.fst_heuristic_forms:
            sources.append("fst_heuristic_forms")
        return tuple(sources)

    @staticmethod
    def _load_lines(path: Path) -> tuple[str, ...]:
        if not path.exists():
            return ()
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, mode="rt", encoding="utf-8") as source:
            return tuple(line.strip() for line in source if line.strip())

    def _prefer_plain_or_gzip(self, filename: str) -> Path:
        plain_path = self.wordlist_dir / filename
        if plain_path.exists():
            return plain_path
        return plain_path.with_suffix(f"{plain_path.suffix}.gz")
