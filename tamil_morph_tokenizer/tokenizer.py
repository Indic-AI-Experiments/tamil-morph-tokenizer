from __future__ import annotations

from dataclasses import dataclass
import regex

from .analysis import (
    MorphAnalysis,
    choose_best_analysis,
    normalize_tag,
)
from .decomposition import ProductiveCompoundLexicon
from .entity import default_entity_analyzer
from .fst import FlookupAnalyzer
from .wordlists import TamilWordLists

TOKENIZATION_MODES = {"best", "compact_ambiguity", "all_analyses"}
UNKNOWN_TAMIL_FALLBACK_MODES = {"unknown_tamil_surface", "grapheme"}
TAMIL_ATOM_PATTERN = r"[\u0B80-\u0B82\u0B84-\u0BFF\p{Mn}\p{Mc}\p{Me}\u200c\u200d]+"
TAMIL_SEGMENT_PATTERN = rf"{TAMIL_ATOM_PATTERN}(?:ஃ{TAMIL_ATOM_PATTERN})*"
TAMIL_INITIAL_PATTERN = r"[\u0B80-\u0BFF][\p{Mn}\p{Mc}\p{Me}\u200c\u200d]*"
WORD_RE = regex.compile(
    rf"""
    \p{{N}}+(?:இலிருந்து|இலிருந்தும்|இல்|ல்|க்கு|ற்கு|ஆல்|உடன்)
    |\p{{N}}+(?:ஆம்|ஆவது|வது|ம்)
    |{TAMIL_SEGMENT_PATTERN}(?:\.{TAMIL_SEGMENT_PATTERN})+\.?
    |(?:{TAMIL_INITIAL_PATTERN}\.){{2,}}
    |{TAMIL_SEGMENT_PATTERN}(?:-{TAMIL_SEGMENT_PATTERN})+
    |{TAMIL_SEGMENT_PATTERN}
    |\p{{N}}+(?:[./:-]\p{{N}}+)+
    |\p{{N}}+(?:[,.]\p{{N}}+)*
    |\p{{Latin}}[\p{{Latin}}\p{{Mn}}\p{{Mc}}\p{{Me}}]*(?:['’.-][\p{{Latin}}\p{{Mn}}\p{{Mc}}\p{{Me}}]+)*
    |\p{{L}}[\p{{L}}\p{{Mn}}\p{{Mc}}\p{{Me}}]*
    |[^\s]
    """,
    regex.VERBOSE,
)
TAMIL_WORD_RE = regex.compile(
    rf"^(?=.*\p{{Tamil}}){TAMIL_SEGMENT_PATTERN}(?:-{TAMIL_SEGMENT_PATTERN})*$"
)
GRAPHEME_RE = regex.compile(r"\X")
PUNCTUATION_RE = regex.compile(r"^\p{P}+$")
SPECIAL_TOKENS = {
    "க்குள்": "<POST_WITHIN_BY>",
    "வரை": "<POST_UNTIL>",
    "முன்": "<POST_BEFORE>",
    "பின்": "<POST_AFTER>",
    "வேண்டும்": "<MODAL_MUST>",
    "மட்டும்": "<PART_ONLY>",
}
READINGS_TOKEN = "<READINGS>"
ALT_TOKEN = "<ALT>"
SUFFIX_HEURISTICS = (
    ("வுக்கு", "<CASE_DAT>"),
    ("வை", "<CASE_ACC>"),
)
NUMERIC_ORDINAL_RE = regex.compile(r"^(?P<number>\p{N}+)(?P<suffix>ஆம்|ஆவது|வது|ம்)$")
NUMERIC_CASE_RE = regex.compile(
    r"^(?P<number>\p{N}+)(?P<suffix>இலிருந்தும்|இலிருந்து|இல்|ல்|க்கு|ற்கு|ஆல்|உடன்)$"
)
DOTTED_TAMIL_ABBREVIATION_RE = regex.compile(
    rf"^(?:(?:{TAMIL_INITIAL_PATTERN}\.){{2,}}|{TAMIL_SEGMENT_PATTERN}(?:\.{TAMIL_SEGMENT_PATTERN})+\.?)$"
)
NUMERIC_CASE_TOKENS = {
    "இலிருந்தும்": ("<CASE_ABL>", "<CLITIC_ADD>"),
    "இலிருந்து": ("<CASE_ABL>",),
    "இல்": ("<CASE_LOC>",),
    "ல்": ("<CASE_LOC>",),
    "க்கு": ("<CASE_DAT>",),
    "ற்கு": ("<CASE_DAT>",),
    "ஆல்": ("<CASE_INST>",),
    "உடன்": ("<CASE_SOC>",),
}


def is_tamil_word(text: str) -> bool:
    return bool(TAMIL_WORD_RE.fullmatch(text))


def unique_in_order(items: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def longest_common_prefix(sequences: tuple[tuple[str, ...], ...]) -> tuple[str, ...]:
    if not sequences:
        return ()
    limit = min(len(sequence) for sequence in sequences)
    index = 0
    while index < limit and len({sequence[index] for sequence in sequences}) == 1:
        index += 1
    return sequences[0][:index]


def encode_readings(
    readings: tuple[tuple[str, ...], ...],
    *,
    common_tokens: tuple[str, ...] = (),
    factor_common: bool = True,
) -> tuple[str, ...]:
    """Encode ordered semantic readings without losing feature co-occurrence."""

    unique = tuple(dict.fromkeys(readings))
    if not unique:
        return common_tokens
    if len(unique) == 1:
        return (*unique[0], *common_tokens)
    common_prefix = longest_common_prefix(unique) if factor_common else ()
    suffixes = tuple(reading[len(common_prefix):] for reading in unique)
    tokens: list[str] = [*common_prefix, *common_tokens, READINGS_TOKEN]
    for index, suffix in enumerate(suffixes):
        if index:
            tokens.append(ALT_TOKEN)
        tokens.extend(suffix)
    return tuple(tokens)


def decode_readings(tokens: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    """Expand the canonical ambiguity grammar into complete semantic readings."""

    if READINGS_TOKEN not in tokens:
        return (tokens,)
    readings_start = tokens.index(READINGS_TOKEN)
    common_prefix = tokens[:readings_start]
    residuals: list[list[str]] = [[]]
    for token in tokens[readings_start + 1:]:
        if token == ALT_TOKEN:
            residuals.append([])
        else:
            residuals[-1].append(token)
    if len(residuals) < 2 or any(not residual for residual in residuals):
        raise ValueError("Malformed ambiguity reading sequence")
    return tuple((*common_prefix, *residual) for residual in residuals)


@dataclass(frozen=True)
class TokenizedWord:
    surface: str
    tokens: tuple[str, ...]
    analyses: tuple[MorphAnalysis, ...]
    best_analysis: MorphAnalysis | None
    fallback: str | None = None
    semantic_special: str | None = None
    special_handling: str | None = None

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def ambiguous(self) -> bool:
        return len(self.analyses) > 1


class TamilMorphTokenizer:
    def __init__(
        self,
        analyzer: FlookupAnalyzer | None = None,
        mode: str = "compact_ambiguity",
        unknown_tamil_fallback: str = "unknown_tamil_surface",
        use_suffix_heuristic: bool = True,
        wordlists: TamilWordLists | None = None,
        compound_lexicon: ProductiveCompoundLexicon | None = None,
        entity_analyzer: object | None = None,
        use_default_entities: bool = True,
    ) -> None:
        if mode not in TOKENIZATION_MODES:
            modes = ", ".join(sorted(TOKENIZATION_MODES))
            raise ValueError(f"Unknown tokenization mode {mode!r}. Expected one of: {modes}")
        if unknown_tamil_fallback not in UNKNOWN_TAMIL_FALLBACK_MODES:
            modes = ", ".join(sorted(UNKNOWN_TAMIL_FALLBACK_MODES))
            raise ValueError(
                f"Unknown Tamil fallback mode {unknown_tamil_fallback!r}. Expected one of: {modes}"
            )
        self.analyzer = analyzer or FlookupAnalyzer()
        self.mode = mode
        self.unknown_tamil_fallback = unknown_tamil_fallback
        self.use_suffix_heuristic = use_suffix_heuristic
        self.wordlists = wordlists or TamilWordLists()
        self.compound_lexicon = compound_lexicon or ProductiveCompoundLexicon()
        self.entity_analyzer = (
            entity_analyzer
            if entity_analyzer is not None or not use_default_entities
            else default_entity_analyzer()
        )

    def split_words(self, text: str) -> list[str]:
        return [match.group(0) for match in WORD_RE.finditer(text)]

    def grapheme_tokens(self, word: str) -> tuple[str, ...]:
        return tuple(GRAPHEME_RE.findall(word))

    def suffix_heuristic_tokens(self, word: str) -> tuple[str, ...] | None:
        for suffix, token in SUFFIX_HEURISTICS:
            if word.endswith(suffix) and len(word) > len(suffix):
                return (word.removesuffix(suffix), token)
        if word.endswith("வில்") and len(word) > len("வில்"):
            base = word.removesuffix("வில்")
            vu_base = f"{base}வு"
            if self.wordlists.contains_lemma(vu_base) or base.endswith("ள"):
                return (vu_base, "<CASE_LOC>")
            if len(self.grapheme_tokens(base)) < 3:
                return None
            if (
                self.wordlists.contains_lemma(base)
                or base.endswith("ா")
            ):
                return (base, "<CASE_LOC>")
        return None

    def structured_fallback_tokens(self, word: str) -> tuple[tuple[str, ...], str] | None:
        ordinal = NUMERIC_ORDINAL_RE.fullmatch(word)
        if ordinal:
            return (ordinal.group("number"), "<NUM_ORDINAL>"), "numeric_ordinal"
        numeric_case = NUMERIC_CASE_RE.fullmatch(word)
        if numeric_case:
            return (
                numeric_case.group("number"),
                *NUMERIC_CASE_TOKENS[numeric_case.group("suffix")],
            ), "numeric_case"

        compact = ""
        if DOTTED_TAMIL_ABBREVIATION_RE.fullmatch(word):
            compact = word.replace(".", "")
        elif "-" in word and all(is_tamil_word(part) for part in word.split("-")):
            compact = word.replace("-", "")
        if not compact:
            return None

        analyze = getattr(self.entity_analyzer, "analyze", None)
        entity_analyses = analyze([compact]).get(compact, ()) if analyze is not None else ()
        best = choose_best_analysis(entity_analyses)
        if best is not None:
            return (
                (*self.analysis_lexical_tokens(best), *best.morph_tokens),
                "orthographic_entity_variant",
            )
        if DOTTED_TAMIL_ABBREVIATION_RE.fullmatch(word):
            return (compact, "<ABBREVIATION>"), "dotted_abbreviation"
        return None

    def analyzed_tokens(
        self,
        word: str,
        analyses: tuple[MorphAnalysis, ...],
        *,
        common_tokens: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        if self.mode == "compact_ambiguity":
            return self.compact_ambiguity_tokens(
                word, analyses, common_tokens=common_tokens
            )
        if self.mode == "all_analyses":
            return self.all_analysis_tokens(word, analyses, common_tokens=common_tokens)
        best = choose_best_analysis(analyses)
        return (
            (*self.analysis_lexical_tokens(best), *best.morph_tokens, *common_tokens)
            if best
            else ()
        )

    def analysis_lexical_tokens(self, analysis: MorphAnalysis) -> tuple[str, ...]:
        normalized_tags = {normalize_tag(tag) for tag in analysis.tags}
        decomposition = self.compound_lexicon.get(analysis.lemma)
        productive_reading = decomposition is not None or (
            "verb" in normalized_tags and "complex" in normalized_tags
        )
        return self.compound_lexicon.semantic_tokens(
            analysis.lemma,
            analysis.morph_tokens,
            productive_reading=productive_reading,
        )

    def ordered_analysis_readings(
        self, analyses: tuple[MorphAnalysis, ...]
    ) -> tuple[tuple[MorphAnalysis, tuple[str, ...]], ...]:
        best = choose_best_analysis(analyses)
        remaining = sorted(
            (analysis for analysis in analyses if analysis != best),
            key=lambda analysis: (
                (*self.analysis_lexical_tokens(analysis), *analysis.morph_tokens),
                analysis.model or "",
                analysis.raw,
            ),
        )
        ordered = (best, *remaining) if best is not None else tuple(remaining)
        readings: list[tuple[MorphAnalysis, tuple[str, ...]]] = []
        seen: set[tuple[str, ...]] = set()
        for analysis in ordered:
            tokens = (*self.analysis_lexical_tokens(analysis), *analysis.morph_tokens)
            if tokens in seen:
                continue
            seen.add(tokens)
            readings.append((analysis, tokens))
        return tuple(readings)

    def compact_ambiguity_tokens(
        self,
        word: str,
        analyses: tuple[MorphAnalysis, ...],
        *,
        common_tokens: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        readings = tuple(tokens for _, tokens in self.ordered_analysis_readings(analyses))
        return encode_readings(readings, common_tokens=common_tokens)

    def all_analysis_tokens(
        self,
        word: str,
        analyses: tuple[MorphAnalysis, ...],
        *,
        common_tokens: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        readings = tuple(tokens for _, tokens in self.ordered_analysis_readings(analyses))
        return encode_readings(
            readings,
            common_tokens=common_tokens,
            factor_common=False,
        )

    def tokenize_word(
        self,
        word: str,
        analyses: tuple[MorphAnalysis, ...],
    ) -> TokenizedWord:
        best = choose_best_analysis(analyses)
        special_token = SPECIAL_TOKENS.get(word)
        if best is not None:
            common_tokens = (special_token,) if special_token else ()
            tokens = self.analyzed_tokens(
                word, analyses, common_tokens=common_tokens
            )
            return TokenizedWord(
                surface=word,
                tokens=tokens,
                analyses=analyses,
                best_analysis=best,
                semantic_special=special_token,
                special_handling="supplement" if special_token else None,
            )
        structured = self.structured_fallback_tokens(word)
        if structured is not None:
            tokens, fallback = structured
            return TokenizedWord(
                surface=word,
                tokens=tokens,
                analyses=(),
                best_analysis=None,
                fallback=fallback,
            )
        if not is_tamil_word(word):
            return TokenizedWord(
                surface=word,
                tokens=(word,),
                analyses=(),
                best_analysis=None,
                fallback="punctuation" if PUNCTUATION_RE.fullmatch(word) else "surface",
            )
        if special_token:
            return TokenizedWord(
                surface=word,
                tokens=(special_token,),
                analyses=analyses,
                best_analysis=None,
                fallback="special",
                semantic_special=special_token,
                special_handling="fallback_override",
            )
        if self.use_suffix_heuristic:
            suffix_tokens = self.suffix_heuristic_tokens(word)
            if suffix_tokens:
                return TokenizedWord(
                    surface=word,
                    tokens=suffix_tokens,
                    analyses=analyses,
                    best_analysis=None,
                    fallback="suffix_heuristic",
                )
        if self.unknown_tamil_fallback == "grapheme":
            return TokenizedWord(
                surface=word,
                tokens=self.grapheme_tokens(word),
                analyses=analyses,
                best_analysis=None,
                fallback="grapheme",
            )
        return TokenizedWord(
            surface=word,
            tokens=(word,),
            analyses=analyses,
            best_analysis=None,
            fallback="unknown_tamil_surface",
        )

    def tokenize(self, text: str) -> list[TokenizedWord]:
        words = self.split_words(text)
        tamil_words = [word for word in words if is_tamil_word(word)]
        analysis_by_word = self.analyzer.analyze(tamil_words) if tamil_words else {}
        if tamil_words and self.entity_analyzer is not None:
            entity_by_word = self.entity_analyzer.analyze(tamil_words)
            analysis_by_word = {
                word: tuple(
                    {
                        analysis.raw: analysis
                        for analysis in (
                            *analysis_by_word.get(word, ()),
                            *entity_by_word.get(word, ()),
                        )
                    }.values()
                )
                for word in tamil_words
            }
        records: list[TokenizedWord] = []
        index = 0
        longest_span = getattr(self.entity_analyzer, "longest_span", None)
        while index < len(words):
            span = longest_span(words, index) if longest_span is not None else None
            if span is not None and span.end - span.start > 1:
                records.append(self.tokenize_word(span.surface, span.analyses))
                index = span.end
                continue
            word = words[index]
            records.append(self.tokenize_word(word, analysis_by_word.get(word, ())))
            index += 1
        return records

    def flat_tokens(self, text: str) -> list[str]:
        flattened: list[str] = []
        for tokenized in self.tokenize(text):
            flattened.extend(tokenized.tokens)
        return flattened

    def token_table(self, text: str) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for tokenized in self.tokenize(text):
            best = tokenized.best_analysis
            rows.append(
                {
                    "surface": tokenized.surface,
                    "mode": self.mode,
                    "tokens": list(tokenized.tokens),
                    "token_text": " ".join(tokenized.tokens),
                    "token_count": tokenized.token_count,
                    "fallback": tokenized.fallback,
                    "semantic_special": tokenized.semantic_special,
                    "special_handling": tokenized.special_handling,
                    "ambiguous": tokenized.ambiguous,
                    "analysis_count": len(tokenized.analyses),
                    "lemma": best.lemma if best else None,
                    "best_analysis": best.raw if best else None,
                    "tags": list(best.tags) if best else [],
                }
            )
        return rows
