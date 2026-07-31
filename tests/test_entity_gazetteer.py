import json

import pytest

from tamil_morph_tokenizer import (
    EntityGazetteer,
    ExactEntityAnalyzer,
    TamilMorphTokenizer,
    StructuredReversibleCodec,
    inflect_entity_form,
)
from tamil_morph_tokenizer.codec import LEXICAL_BYTES_END, LEXICAL_BYTES_START, SURFACE_BYTES
from tamil_morph_tokenizer.analysis import parse_analysis


class StaticAnalyzer:
    def __init__(self, analyses_by_word=None):
        self.analyses_by_word = analyses_by_word or {}

    def analyze(self, words):
        return {
            word: tuple(parse_analysis(raw, model="core-test") for raw in self.analyses_by_word.get(word, ()))
            for word in words
        }


def write_rows(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def reviewed_city():
    return {
        "lemma": "சென்னை",
        "entity_type": "city",
        "aliases": [{"surface": "மெட்ராஸ்", "declension": "consonant"}],
        "declension": "vowel_y",
        "sources": ["gold-test-fixture"],
        "review_status": "reviewed",
        "entity_id": "test:city:chennai",
    }


def test_reviewed_exact_entity_emits_canonical_lemma_and_specific_type(tmp_path):
    path = tmp_path / "entities.jsonl"
    write_rows(path, [reviewed_city()])
    entity_analyzer = ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path))
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(), mode="best", entity_analyzer=entity_analyzer
    )

    record = tokenizer.tokenize("மெட்ராஸ்")[0]

    assert record.tokens == ("மெட்ராஸ்", "<ENTITY_CITY>", "<CASE_NOM>")
    assert record.best_analysis.raw == "மெட்ராஸ்+entity_city+nom"
    assert record.best_analysis.model == "entity-gazetteer"


@pytest.mark.parametrize(
    ("surface", "declension", "expected"),
    [
        ("இந்தியா", "vowel_v", {"acc": "இந்தியாவை", "loc": "இந்தியாவில்"}),
        ("சென்னை", "vowel_y", {"dat": "சென்னைக்கு", "abl": "சென்னையிலிருந்து"}),
        ("கேரளம்", "m_final", {"acc": "கேரளத்தை", "loc": "கேரளத்தில்"}),
        ("ஜப்பான்", "consonant", {"gen": "ஜப்பானின்", "soc": "ஜப்பானுடன்"}),
        ("தமிழ்நாடு", "du_geminate", {"acc": "தமிழ்நாட்டை", "loc": "தமிழ்நாட்டில்"}),
        ("ஆறு", "ru_geminate", {"dat": "ஆற்றுக்கு", "abl": "ஆற்றிலிருந்து"}),
    ],
)
def test_declension_templates_generate_reviewed_case_paradigms(surface, declension, expected):
    forms = inflect_entity_form(surface, declension)
    assert {case: forms[case] for case in expected} == expected


def test_inflected_entity_emits_alias_lemma_type_and_case(tmp_path):
    path = tmp_path / "entities.jsonl"
    write_rows(path, [reviewed_city()])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        mode="best",
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )

    record = tokenizer.tokenize("மெட்ராஸில்")[0]

    assert record.tokens == ("மெட்ராஸ்", "<ENTITY_CITY>", "<CASE_LOC>")
    assert record.best_analysis.raw == "மெட்ராஸ்+entity_city+loc"


def test_common_word_entity_ambiguity_is_preserved(tmp_path):
    row = {
        "lemma": "ரோஜா",
        "entity_type": "person",
        "aliases": [],
        "declension": "vowel_v",
        "sources": ["gold-test-fixture"],
        "review_status": "reviewed",
    }
    path = tmp_path / "entities.jsonl"
    write_rows(path, [row])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer({"ரோஜா": ("ரோஜா+noun+nom",)}),
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )

    record = tokenizer.tokenize("ரோஜா")[0]

    assert {analysis.raw for analysis in record.analyses} == {
        "ரோஜா+noun+nom",
        "ரோஜா+entity_person+nom",
    }
    assert "<POS_NOUN>" in record.tokens
    assert "<ENTITY_PERSON>" in record.tokens


def test_candidate_and_rejected_rows_are_not_runtime_entities(tmp_path):
    candidate = reviewed_city() | {"review_status": "candidate"}
    path = tmp_path / "entities.jsonl"
    write_rows(path, [candidate])
    gazetteer = EntityGazetteer.from_jsonl(path)
    assert gazetteer.exact_matches("சென்னை") == ()


def test_grantha_spelling_does_not_infer_an_entity(tmp_path):
    path = tmp_path / "entities.jsonl"
    write_rows(path, [reviewed_city()])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )
    record = tokenizer.tokenize("பொலிஸ்")[0]
    assert not any("ENTITY" in token for token in record.tokens)
    assert record.fallback == "unknown_tamil_surface"


def test_invalid_or_unproven_entries_fail_closed(tmp_path):
    path = tmp_path / "entities.jsonl"
    write_rows(path, [reviewed_city() | {"sources": []}])
    with pytest.raises(ValueError, match="sources"):
        EntityGazetteer.from_jsonl(path)

    write_rows(path, [reviewed_city() | {"entity_type": "company"}])
    with pytest.raises(ValueError, match="entity_type"):
        EntityGazetteer.from_jsonl(path)

    write_rows(path, [reviewed_city() | {"declension": "ai_final"}])
    with pytest.raises(ValueError, match="declension"):
        EntityGazetteer.from_jsonl(path)


def test_longest_multiword_entity_span_carries_final_word_case(tmp_path):
    path = tmp_path / "entities.jsonl"
    row = {
        "lemma": "இந்திய தேசிய காங்கிரஸ்",
        "entity_type": "org",
        "aliases": [
            {"surface": "காங்கிரஸ்", "declension": "consonant"},
        ],
        "declension": "consonant",
        "sources": ["gold-test-fixture"],
        "review_status": "reviewed",
        "entity_id": "test:org:inc",
    }
    write_rows(path, [row])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        mode="best",
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )

    records = tokenizer.tokenize("இந்திய தேசிய காங்கிரஸின் தலைவர்")

    assert records[0].surface == "இந்திய தேசிய காங்கிரஸின்"
    assert records[0].tokens == (
        "இந்திய தேசிய காங்கிரஸ்",
        "<ENTITY_ORG>",
        "<CASE_GEN>",
    )
    assert records[1].surface == "தலைவர்"


def test_phrase_matcher_prefers_longest_reviewed_span(tmp_path):
    path = tmp_path / "entities.jsonl"
    rows = [
        {
            "lemma": "தமிழ்நாடு",
            "entity_type": "region",
            "aliases": [],
            "declension": "du_geminate",
            "sources": ["gold-test-fixture"],
            "review_status": "reviewed",
        },
        {
            "lemma": "தமிழ்நாடு அரசு",
            "entity_type": "org",
            "aliases": [],
            "declension": "u_drop",
            "sources": ["gold-test-fixture"],
            "review_status": "reviewed",
        },
    ]
    write_rows(path, rows)
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        mode="best",
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )

    records = tokenizer.tokenize("தமிழ்நாடு அரசால் அறிவிக்கப்பட்டது")

    assert records[0].surface == "தமிழ்நாடு அரசால்"
    assert records[0].best_analysis.raw == "தமிழ்நாடு அரசு+entity_org+inst"


def test_inflected_entity_round_trips_without_surface_duplication(tmp_path):
    path = tmp_path / "entities.jsonl"
    write_rows(path, [reviewed_city()])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        mode="best",
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )
    codec = StructuredReversibleCodec(tokenizer=tokenizer)

    encoding = codec.encode("மெட்ராஸில்")

    assert encoding.spans[0].semantic_tokens == (
        "மெட்ராஸ்",
        "<ENTITY_CITY>",
        "<CASE_LOC>",
    )
    assert LEXICAL_BYTES_START in encoding.tokens
    assert LEXICAL_BYTES_END in encoding.tokens
    assert SURFACE_BYTES not in encoding.tokens
    assert "மெட்ராஸில்" not in encoding.tokens
    assert codec.decode_tokens(encoding.tokens) == "மெட்ராஸில்"


def test_multiword_entity_round_trips_as_one_semantic_span(tmp_path):
    path = tmp_path / "entities.jsonl"
    row = {
        "lemma": "இந்திய தேசிய காங்கிரஸ்",
        "entity_type": "org",
        "aliases": [],
        "declension": "consonant",
        "sources": ["gold-test-fixture"],
        "review_status": "reviewed",
    }
    write_rows(path, [row])
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(),
        mode="best",
        entity_analyzer=ExactEntityAnalyzer(EntityGazetteer.from_jsonl(path)),
    )
    codec = StructuredReversibleCodec(tokenizer=tokenizer)

    encoding = codec.encode("இந்திய தேசிய காங்கிரஸின் தலைவர்")

    assert encoding.spans[0].surface == "இந்திய தேசிய காங்கிரஸின்"
    assert encoding.spans[0].semantic_tokens == (
        "இந்திய தேசிய காங்கிரஸ்",
        "<ENTITY_ORG>",
        "<CASE_GEN>",
    )
    assert SURFACE_BYTES not in encoding.spans[0].tokens
    assert codec.decode(encoding) == "இந்திய தேசிய காங்கிரஸின் தலைவர்"
