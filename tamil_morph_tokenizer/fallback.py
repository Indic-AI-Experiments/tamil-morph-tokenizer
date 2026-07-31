from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
import unicodedata

import regex

from .fst import PACKAGE_DIR


DEFAULT_TAMIL_GRAPHEME_PATH = (
    PACKAGE_DIR / "data" / "vocabulary" / "tamil_graphemes.txt"
)
GRAPHEME_RE = regex.compile(r"\X")
TAMIL_LEXICAL_RE = regex.compile(
    r"^(?=.*\p{Tamil})[\p{Tamil}\p{M}\u200c\u200d-]+$"
)
TAMIL_GRAPHEME_TOKEN_RE = re.compile(
    r"^<TAMIL_GRAPHEME_(U[0-9A-F]{4,6}(?:_U[0-9A-F]{4,6})*)>$"
)

# Tamil consonants, including the Grantha letters used in contemporary Tamil.
TAMIL_CONSONANTS = tuple("கஙசஞடணதநபமயரலவழளறனஜஷஸஹஶ")


def tamil_grapheme_token(grapheme: str) -> str:
    codepoints = "_".join(f"U{ord(character):04X}" for character in grapheme)
    return f"<TAMIL_GRAPHEME_{codepoints}>"


def decode_tamil_grapheme_token(token: str) -> str:
    match = TAMIL_GRAPHEME_TOKEN_RE.fullmatch(token)
    if match is None:
        raise ValueError(f"Not a Tamil grapheme token: {token}")
    return "".join(chr(int(value[1:], 16)) for value in match.group(1).split("_"))


def build_tamil_grapheme_inventory(
    lexical_strings: set[str] | tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Build a corpus-independent alphabet for ordinary reversible Tamil fallback."""

    inventory = {
        grapheme
        for lexical in lexical_strings
        if TAMIL_LEXICAL_RE.fullmatch(lexical)
        for grapheme in GRAPHEME_RE.findall(lexical)
    }
    inventory.update(
        chr(codepoint)
        for codepoint in range(0x0B80, 0x0C00)
        if unicodedata.category(chr(codepoint)) != "Cn"
    )
    dependent_marks = tuple(
        chr(codepoint)
        for codepoint in range(0x0BBE, 0x0BCE)
        if unicodedata.category(chr(codepoint)).startswith("M")
    )
    for consonant in TAMIL_CONSONANTS:
        inventory.update(consonant + mark for mark in dependent_marks)
        # Preserve the canonically decomposed AU spelling as an exact grapheme too.
        inventory.add(consonant + "ெ" + "ௗ")
    return tuple(
        sorted(inventory, key=lambda value: tuple(ord(character) for character in value))
    )


@lru_cache(maxsize=None)
def load_tamil_graphemes(
    path: str | Path = DEFAULT_TAMIL_GRAPHEME_PATH,
) -> frozenset[str]:
    return frozenset(Path(path).read_text(encoding="utf-8").splitlines())


def encode_tamil_graphemes(
    text: str,
    *,
    inventory: frozenset[str] | None = None,
) -> tuple[str, ...] | None:
    """Return exact fixed-vocabulary grapheme tokens, or None for byte escape."""

    allowed = load_tamil_graphemes() if inventory is None else inventory
    graphemes = tuple(GRAPHEME_RE.findall(text))
    if any(grapheme not in allowed for grapheme in graphemes):
        return None
    return tuple(tamil_grapheme_token(grapheme) for grapheme in graphemes)
