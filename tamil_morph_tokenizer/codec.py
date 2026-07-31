from __future__ import annotations

from dataclasses import dataclass, replace
import re

from .analysis import MorphAnalysis, choose_best_analysis, normalize_tag, parse_analysis
from .entity import ENTITY_CASES, ENTITY_TYPES
from .fallback import (
    TAMIL_GRAPHEME_TOKEN_RE,
    decode_tamil_grapheme_token,
    encode_tamil_graphemes,
)
from .fst import DEFAULT_MODEL_ORDER
from .realization import RealizationDecision, RealizationSelector
from .signature import TagSignatureCodebook
from .tokenizer import (
    SPECIAL_TOKENS,
    TamilMorphTokenizer,
    TokenizedWord,
    WORD_RE,
    decode_readings,
    encode_readings,
    is_tamil_word,
)
from .vocabulary import FixedVocabulary


WORD_START = "<WORD_START>"
SURFACE_BYTES = "<SURFACE_BYTES>"
FST_LEMMA_BYTES_START = "<FST_LEMMA_BYTES_START>"
FST_LEMMA_BYTES_END = "<FST_LEMMA_BYTES_END>"
LEXICAL_BYTES_START = "<LEXICAL_BYTES_START>"
LEXICAL_BYTES_END = "<LEXICAL_BYTES_END>"
BYTE_TOKEN_RE = re.compile(r"^<BYTE_([0-9A-F]{2})>$")
REALIZATION_TOKEN_RE = re.compile(r"^<REALIZATION_([1-9][0-9]*)>$")
COMPOUND_VARIANT_TOKEN_RE = re.compile(r"^<COMPOUND_VARIANT_([1-9][0-9]*)>$")
TAG_VARIANT_TOKEN_RE = re.compile(r"^<TAG_VARIANT_([1-9][0-9]*)>$")
COMPOUND_VARIANT_TOKENS = tuple(f"<COMPOUND_VARIANT_{index}>" for index in range(1, 3))
MODEL_TO_TOKEN = {
    model: f"<FST_MODEL_{model.removesuffix('.fst').upper().replace('-', '_')}>"
    for model in DEFAULT_MODEL_ORDER
}
MODEL_TO_TOKEN["entity-gazetteer"] = "<ENTITY_GAZETTEER_MODEL>"
TOKEN_TO_MODEL = {token: model for model, token in MODEL_TO_TOKEN.items()}
ENTITY_TOKEN_TO_TYPE = {
    f"<ENTITY_{entity_type.upper()}>": entity_type for entity_type in ENTITY_TYPES
}
CASE_TOKEN_TO_TAG = {f"<CASE_{case.upper()}>": case for case in ENTITY_CASES}


def encode_utf8_bytes(text: str) -> tuple[str, ...]:
    return tuple(f"<BYTE_{byte:02X}>" for byte in text.encode("utf-8"))


def decode_utf8_bytes(tokens: tuple[str, ...] | list[str]) -> str:
    values: list[int] = []
    for token in tokens:
        match = BYTE_TOKEN_RE.fullmatch(token)
        if match is None:
            raise ValueError(f"Not a UTF-8 byte token: {token}")
        values.append(int(match.group(1), 16))
    return bytes(values).decode("utf-8")


@dataclass(frozen=True)
class ReversibleSpan:
    surface: str
    start: int
    end: int
    kind: str
    semantic_tokens: tuple[str, ...]
    tokens: tuple[str, ...]
    analyses: tuple[MorphAnalysis, ...] = ()
    selected_analysis: MorphAnalysis | None = None
    realization: RealizationDecision | None = None
    fallback: str | None = None

    @property
    def lemma(self) -> str | None:
        return self.semantic_tokens[0] if self.selected_analysis and self.semantic_tokens else None

    @property
    def fst_lemma(self) -> str | None:
        return self.selected_analysis.lemma if self.selected_analysis else None

    def to_dict(self) -> dict[str, object]:
        return {
            "surface": self.surface,
            "span": {"start": self.start, "end": self.end},
            "kind": self.kind,
            "lemma": self.lemma,
            "fst_lemma": self.fst_lemma,
            "tokens": list(self.tokens),
            "selected_analysis": self.selected_analysis.raw if self.selected_analysis else None,
            "analyses": [analysis.raw for analysis in self.analyses],
            "realization": None if self.realization is None else {
                "strategy": self.realization.strategy,
                "candidates": list(self.realization.candidates),
                "selected_index": self.realization.selected_index,
                "tokens": list(self.realization.tokens),
                "exact": self.realization.exact,
            },
            "fallback": self.fallback,
        }


@dataclass(frozen=True)
class ReversibleEncoding:
    spans: tuple[ReversibleSpan, ...]
    tokens: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "tokens": list(self.tokens),
            "spans": [span.to_dict() for span in self.spans],
        }


class StructuredReversibleCodec:
    """Surface-free morphology codec with an independently decodable token stream."""

    def __init__(
        self,
        tokenizer: TamilMorphTokenizer | None = None,
        realization_selector: RealizationSelector | None = None,
        tag_codebook: TagSignatureCodebook | None = None,
    ) -> None:
        self.tokenizer = tokenizer or TamilMorphTokenizer()
        self.realization_selector = realization_selector or RealizationSelector()
        self.tag_codebook = tag_codebook or TagSignatureCodebook()

    @staticmethod
    def split_spans(text: str) -> tuple[tuple[str, int, int], ...]:
        spans: list[tuple[str, int, int]] = []
        cursor = 0
        for match in WORD_RE.finditer(text):
            if match.start() > cursor:
                spans.append((text[cursor:match.start()], cursor, match.start()))
            spans.append((match.group(0), match.start(), match.end()))
            cursor = match.end()
        if cursor < len(text):
            spans.append((text[cursor:], cursor, len(text)))
        return tuple(spans)

    def encode(self, text: str) -> ReversibleEncoding:
        return self.encode_records(text, self.tokenizer.tokenize(text))

    def encode_records(
        self,
        text: str,
        records: tuple[TokenizedWord, ...] | list[TokenizedWord],
    ) -> ReversibleEncoding:
        """Encode precomputed records without repeating FST analysis."""

        spans: list[ReversibleSpan] = []
        all_tokens: list[str] = []
        cursor = 0
        for record in records:
            start = text.find(record.surface, cursor)
            if start < 0:
                raise ValueError(
                    f"Tokenizer surface is not aligned with input: {record.surface!r}"
                )
            if start > cursor:
                gap = text[cursor:start]
                gap_span = self._byte_span(
                    gap,
                    cursor,
                    start,
                    "whitespace" if gap.isspace() else "byte_fallback",
                )
                spans.append(gap_span)
                all_tokens.extend(gap_span.tokens)
            surface = record.surface
            end = start + len(surface)
            analyses = record.analyses
            selected = record.best_analysis or choose_best_analysis(analyses)
            if selected is not None:
                reversible_model = next(
                    (
                        model
                        for model in (selected.model or "").split("|")
                        if model in MODEL_TO_TOKEN
                    ),
                    None,
                )
                if reversible_model is None:
                    raise ValueError(
                        f"Analyzed word has no supported FST model: {selected.raw!r}"
                    )
                reversible_analysis = replace(selected, model=reversible_model)
                lexical_tokens = self.tokenizer.analysis_lexical_tokens(selected)
                semantic_tokens = (*lexical_tokens, *selected.morph_tokens)
                special_token = SPECIAL_TOKENS.get(surface)
                if special_token and special_token not in semantic_tokens:
                    semantic_tokens = (*semantic_tokens, special_token)
                signature_tokens = self._signature_tokens(reversible_analysis, lexical_tokens)
                realization = (
                    self._entity_realization(surface, reversible_analysis)
                    if reversible_model == "entity-gazetteer"
                    else self.realization_selector.select(surface, reversible_analysis)
                )
                stream_semantic_tokens = self._stream_analysis_readings(
                    analyses,
                    selected,
                    special_token,
                )
                if realization.exact:
                    stream_tokens = (
                        WORD_START,
                        *stream_semantic_tokens,
                        *signature_tokens,
                        *realization.tokens,
                    )
                    span = ReversibleSpan(
                        surface=surface,
                        start=start,
                        end=end,
                        kind="analyzed",
                        semantic_tokens=semantic_tokens,
                        tokens=stream_tokens,
                        analyses=analyses,
                        selected_analysis=selected,
                        realization=realization,
                    )
                else:
                    byte_tokens = encode_utf8_bytes(surface)
                    stream_tokens = (
                        WORD_START,
                        *stream_semantic_tokens,
                        *signature_tokens,
                        SURFACE_BYTES,
                        *byte_tokens,
                    )
                    span = ReversibleSpan(
                        surface=surface,
                        start=start,
                        end=end,
                        kind="analyzed_byte_fallback",
                        semantic_tokens=semantic_tokens,
                        tokens=stream_tokens,
                        analyses=analyses,
                        selected_analysis=selected,
                        realization=realization,
                        fallback="surface_bytes",
                    )
            else:
                if record.fallback in {
                    "numeric_ordinal",
                    "numeric_case",
                    "dotted_abbreviation",
                    "orthographic_entity_variant",
                }:
                    span = self._semantic_byte_span(
                        surface, start, end, record.tokens, record.fallback
                    )
                elif is_tamil_word(surface):
                    grapheme_tokens = encode_tamil_graphemes(surface)
                    span = (
                        self._tamil_grapheme_span(
                            surface,
                            start,
                            end,
                            grapheme_tokens,
                            analyses,
                        )
                        if grapheme_tokens is not None
                        else self._byte_span(
                            surface, start, end, "byte_fallback", analyses
                        )
                    )
                else:
                    span = self._byte_span(surface, start, end, "byte_fallback", analyses)
            spans.append(span)
            all_tokens.extend(span.tokens)
            cursor = end

        if cursor < len(text):
            gap = text[cursor:]
            gap_span = self._byte_span(
                gap,
                cursor,
                len(text),
                "whitespace" if gap.isspace() else "byte_fallback",
            )
            spans.append(gap_span)
            all_tokens.extend(gap_span.tokens)

        return ReversibleEncoding(tuple(spans), tuple(all_tokens))

    @staticmethod
    def _byte_span(
        surface: str,
        start: int,
        end: int,
        kind: str,
        analyses: tuple[MorphAnalysis, ...] = (),
    ) -> ReversibleSpan:
        stream_tokens = encode_utf8_bytes(surface)
        return ReversibleSpan(
            surface=surface,
            start=start,
            end=end,
            kind=kind,
            semantic_tokens=(),
            tokens=stream_tokens,
            analyses=analyses,
            fallback="utf8_bytes",
        )

    @staticmethod
    def _tamil_grapheme_span(
        surface: str,
        start: int,
        end: int,
        grapheme_tokens: tuple[str, ...],
        analyses: tuple[MorphAnalysis, ...] = (),
    ) -> ReversibleSpan:
        stream_tokens = (WORD_START, *grapheme_tokens)
        return ReversibleSpan(
            surface=surface,
            start=start,
            end=end,
            kind="tamil_grapheme_fallback",
            semantic_tokens=grapheme_tokens,
            tokens=stream_tokens,
            analyses=analyses,
            fallback="tamil_graphemes",
        )

    @staticmethod
    def _semantic_byte_span(
        surface: str,
        start: int,
        end: int,
        semantic_tokens: tuple[str, ...],
        fallback: str,
    ) -> ReversibleSpan:
        stream_tokens = (
            WORD_START,
            *semantic_tokens,
            SURFACE_BYTES,
            *encode_utf8_bytes(surface),
        )
        return ReversibleSpan(
            surface=surface,
            start=start,
            end=end,
            kind="structured_byte_fallback",
            semantic_tokens=semantic_tokens,
            tokens=stream_tokens,
            fallback=fallback,
        )

    @staticmethod
    def _stream_semantic_tokens(
        semantic_tokens: tuple[str, ...], analysis: MorphAnalysis
    ) -> tuple[str, ...]:
        if analysis.model != "entity-gazetteer":
            return semantic_tokens
        return (
            LEXICAL_BYTES_START,
            *encode_utf8_bytes(analysis.lemma),
            LEXICAL_BYTES_END,
            *semantic_tokens[1:],
        )

    def _stream_analysis_readings(
        self,
        analyses: tuple[MorphAnalysis, ...],
        selected: MorphAnalysis,
        special_token: str | None,
    ) -> tuple[str, ...]:
        if self.tokenizer.mode == "best":
            semantic_tokens = (
                *self.tokenizer.analysis_lexical_tokens(selected),
                *selected.morph_tokens,
            )
            streamed = self._stream_semantic_tokens(semantic_tokens, selected)
            return (*streamed, *((special_token,) if special_token else ()))

        ordered = self.tokenizer.ordered_analysis_readings(analyses)
        streamed_readings = tuple(
            self._stream_semantic_tokens(tokens, analysis)
            for analysis, tokens in ordered
        )
        return encode_readings(
            streamed_readings,
            common_tokens=(special_token,) if special_token else (),
            factor_common=self.tokenizer.mode == "compact_ambiguity",
        )

    def _entity_realization(
        self, surface: str, analysis: MorphAnalysis
    ) -> RealizationDecision:
        normalized = tuple(normalize_tag(tag) for tag in analysis.tags)
        entity_type = next(
            (tag.removeprefix("entity_") for tag in normalized if tag.startswith("entity_")),
            None,
        )
        case = next((tag for tag in normalized if tag in ENTITY_CASES), None)
        realize = getattr(self.tokenizer.entity_analyzer, "realize", None)
        candidate = (
            realize(analysis.lemma, entity_type, case)
            if realize is not None and entity_type is not None and case is not None
            else None
        )
        candidates = (candidate,) if candidate is not None else ()
        exact = candidate == surface
        return RealizationDecision(
            strategy="entity_template" if exact else "byte_fallback",
            candidates=candidates,
            selected_index=0 if exact else None,
            tokens=(),
            exact=exact,
        )

    def _signature_tokens(
        self,
        analysis: MorphAnalysis,
        lexical_tokens: tuple[str, ...],
    ) -> tuple[str, ...]:
        model_tokens = tuple(
            MODEL_TO_TOKEN[model]
            for model in (analysis.model or "").split("|")
            if model in MODEL_TO_TOKEN
        )[:1]
        if not model_tokens:
            raise ValueError(f"Analyzed word has no supported FST model: {analysis.raw!r}")
        model = TOKEN_TO_MODEL[model_tokens[0]]
        if model == "entity-gazetteer":
            return model_tokens
        _, separator, raw_tags = analysis.raw.partition("+")
        raw_tags = raw_tags if separator else ""
        tag_variant = self.tag_codebook.variant_for(
            model,
            analysis.morph_tokens,
            raw_tags,
        )
        tag_variant_tokens = (f"<TAG_VARIANT_{tag_variant}>",) if tag_variant else ()
        raw_lemma_tokens: tuple[str, ...] = ()
        if analysis.lemma != lexical_tokens[0]:
            compound_candidates = self.tokenizer.compound_lexicon.compound_lemmas(
                lexical_tokens,
                analysis.morph_tokens,
            )
            if analysis.lemma in compound_candidates:
                selected_index = compound_candidates.index(analysis.lemma)
                if selected_index:
                    raw_lemma_tokens = (f"<COMPOUND_VARIANT_{selected_index}>",)
            else:
                raw_lemma_tokens = (
                    FST_LEMMA_BYTES_START,
                    *encode_utf8_bytes(analysis.lemma),
                    FST_LEMMA_BYTES_END,
                )
        return (
            *model_tokens,
            *raw_lemma_tokens,
            *tag_variant_tokens,
        )

    def decode(self, encoding: ReversibleEncoding) -> str:
        return self.decode_tokens(encoding.tokens)

    def decode_tokens(self, stream: tuple[str, ...] | list[str]) -> str:
        decoded: list[str] = []
        tokens = tuple(stream)
        cursor = 0
        while cursor < len(tokens):
            if BYTE_TOKEN_RE.fullmatch(tokens[cursor]):
                end = cursor + 1
                while end < len(tokens) and BYTE_TOKEN_RE.fullmatch(tokens[end]):
                    end += 1
                decoded.append(decode_utf8_bytes(tokens[cursor:end]))
                cursor = end
                continue
            if tokens[cursor] != WORD_START:
                raise ValueError(f"Expected a span boundary, got: {tokens[cursor]}")

            next_word = len(tokens)
            try:
                next_word = tokens.index(WORD_START, cursor + 1)
            except ValueError:
                pass
            word_region = tokens[cursor + 1:next_word]
            if not word_region:
                raise ValueError("Empty analyzed-word span")
            if TAMIL_GRAPHEME_TOKEN_RE.fullmatch(word_region[0]):
                grapheme_end = 0
                while (
                    grapheme_end < len(word_region)
                    and TAMIL_GRAPHEME_TOKEN_RE.fullmatch(word_region[grapheme_end])
                ):
                    grapheme_end += 1
                decoded.append(
                    "".join(
                        decode_tamil_grapheme_token(token)
                        for token in word_region[:grapheme_end]
                    )
                )
                cursor += grapheme_end + 1
                continue
            if SURFACE_BYTES in word_region:
                byte_start = word_region.index(SURFACE_BYTES) + 1
                decoded.append(decode_utf8_bytes(word_region[byte_start:]))
                cursor = next_word
                continue

            model_start = self._find_model_token(word_region)
            end = self._signature_payload_end(word_region, model_start)
            while end < len(word_region) and REALIZATION_TOKEN_RE.fullmatch(
                word_region[end]
            ):
                end += 1
            word_tokens = word_region[:end]
            decoded.append(self._decode_analyzed_word(word_tokens))
            cursor += end + 1
        return "".join(decoded)

    def decode_ids(
        self,
        input_ids: tuple[int, ...] | list[int],
        vocabulary: FixedVocabulary,
    ) -> str:
        return self.decode_tokens(vocabulary.decode(input_ids))

    def _decode_analyzed_word(self, tokens: tuple[str, ...]) -> str:
        signature_start = self._find_model_token(tokens)
        signature_end = self._signature_payload_end(tokens, signature_start)
        semantic_region = tokens[:signature_start]
        selected_tokens = self._selected_reading_tokens(semantic_region)
        special_tokens = set(SPECIAL_TOKENS.values())
        while selected_tokens and selected_tokens[0] in special_tokens:
            selected_tokens = selected_tokens[1:]
        if not selected_tokens:
            raise ValueError("Analyzed word is missing its lemma token")

        lexical_bytes = selected_tokens[0] == LEXICAL_BYTES_START
        if lexical_bytes:
            lexical_end = self._find_token(selected_tokens, LEXICAL_BYTES_END, 1)
            lemma = decode_utf8_bytes(selected_tokens[1:lexical_end])
            lexical_token_end = lexical_end + 1
        else:
            lemma = selected_tokens[0]
            lexical_token_end = 1
        signature_prefix = tokens[signature_start:signature_end]
        compound_variant = 0
        tag_variant = 0
        raw_lemma_encoded = FST_LEMMA_BYTES_START in signature_prefix
        if raw_lemma_encoded:
            lemma_start = signature_prefix.index(FST_LEMMA_BYTES_START)
            lemma_end = signature_prefix.index(FST_LEMMA_BYTES_END, lemma_start + 1)
            lemma = decode_utf8_bytes(signature_prefix[lemma_start + 1:lemma_end])
            residual_tokens = (
                *signature_prefix[:lemma_start],
                *signature_prefix[lemma_end + 1:],
            )
        else:
            residual_tokens = signature_prefix
            for token in signature_prefix:
                match = COMPOUND_VARIANT_TOKEN_RE.fullmatch(token)
                if match is not None:
                    compound_variant = int(match.group(1))
                    break
        model_tokens = tuple(
            token for token in residual_tokens
            if token in TOKEN_TO_MODEL
        )
        for token in residual_tokens:
            match = TAG_VARIANT_TOKEN_RE.fullmatch(token)
            if match is not None:
                tag_variant = int(match.group(1))
                break
        models: list[str] = []
        for token in model_tokens:
            model = TOKEN_TO_MODEL.get(token)
            if model is None:
                raise ValueError(f"Unknown FST model token: {token}")
            models.append(model)
        if len(models) != 1:
            raise ValueError(f"Expected one FST model token, got: {models!r}")
        if models[0] == "entity-gazetteer":
            morph_tokens = selected_tokens[lexical_token_end:]
            entity_type = next(
                (
                    ENTITY_TOKEN_TO_TYPE[token]
                    for token in morph_tokens
                    if token in ENTITY_TOKEN_TO_TYPE
                ),
                None,
            )
            case = next(
                (CASE_TOKEN_TO_TAG[token] for token in morph_tokens if token in CASE_TOKEN_TO_TAG),
                None,
            )
            realize = getattr(self.tokenizer.entity_analyzer, "realize", None)
            surface = (
                realize(lemma, entity_type, case)
                if realize is not None and entity_type is not None and case is not None
                else None
            )
            if surface is None:
                raise ValueError(f"Entity realization is unavailable for {lemma!r}")
            return surface
        _, compound_length = self.tokenizer.compound_lexicon.match_compound_tokens(
            selected_tokens
        )
        selected_index = 0
        for token in tokens[signature_end:]:
            match = REALIZATION_TOKEN_RE.fullmatch(token)
            if match is not None:
                selected_index = int(match.group(1))
                break

        lexical_lengths = (1,) if raw_lemma_encoded else tuple(
            dict.fromkeys((1, compound_length) if compound_length > 1 else (1,))
        )
        attempted: list[str] = []
        for lexical_length in lexical_lengths:
            morph_tokens = tuple(selected_tokens[lexical_length:])
            candidate_lemma = lemma
            if not raw_lemma_encoded:
                compound_candidates = self.tokenizer.compound_lexicon.compound_lemmas(
                    selected_tokens[:lexical_length],
                    morph_tokens,
                )
                if compound_candidates:
                    if compound_variant >= len(compound_candidates):
                        continue
                    candidate_lemma = compound_candidates[compound_variant]
                elif lexical_length != 1:
                    continue
            raw_tags = None
            morph_variants = tuple(dict.fromkeys((
                morph_tokens,
                tuple(token for token in morph_tokens if token not in special_tokens),
            )))
            for variant in morph_variants:
                try:
                    raw_tags = self.tag_codebook.raw_tags(
                        models[0],
                        variant,
                        tag_variant,
                    )
                    break
                except ValueError:
                    continue
            if raw_tags is None:
                continue
            raw_analysis = candidate_lemma + (f"+{raw_tags}" if raw_tags else "")
            attempted.append(raw_analysis)
            analysis = parse_analysis(raw_analysis, model=models[0])
            candidates = self.realization_selector.generator.generate(analysis)
            if 0 <= selected_index < len(candidates):
                return candidates[selected_index]
        raise ValueError(
            f"No reversible analysis for {selected_tokens[0]!r}; attempted: {attempted!r}"
        )

    @staticmethod
    def _selected_reading_tokens(tokens: tuple[str, ...]) -> tuple[str, ...]:
        return decode_readings(tokens)[0]

    @staticmethod
    def _find_token(
        tokens: tuple[str, ...],
        target: str,
        start: int = 0,
    ) -> int:
        try:
            return tokens.index(target, start)
        except ValueError as exc:
            raise ValueError(f"Missing structural token: {target}") from exc

    @staticmethod
    def _find_model_token(tokens: tuple[str, ...]) -> int:
        for index, token in enumerate(tokens):
            if token in TOKEN_TO_MODEL:
                return index
        raise ValueError("Missing FST model token")

    @classmethod
    def _signature_payload_end(
        cls,
        tokens: tuple[str, ...],
        model_start: int,
    ) -> int:
        cursor = model_start + 1
        if cursor < len(tokens) and tokens[cursor] == FST_LEMMA_BYTES_START:
            cursor = cls._find_token(tokens, FST_LEMMA_BYTES_END, cursor + 1) + 1
        elif cursor < len(tokens) and COMPOUND_VARIANT_TOKEN_RE.fullmatch(tokens[cursor]):
            cursor += 1
        if cursor < len(tokens) and TAG_VARIANT_TOKEN_RE.fullmatch(tokens[cursor]):
            cursor += 1
        return cursor
