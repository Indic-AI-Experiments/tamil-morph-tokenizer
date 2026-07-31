from pathlib import Path
import shutil

import pytest

from tamil_morph_tokenizer import TamilMorphTokenizer
from tamil_morph_tokenizer.analysis import parse_analysis
from tamil_morph_tokenizer.tokenizer import decode_readings, encode_readings, is_tamil_word


class StaticAnalyzer:
    def __init__(self, analyses_by_word):
        self.analyses_by_word = analyses_by_word

    def analyze(self, words):
        return {
            word: tuple(parse_analysis(raw) for raw in self.analyses_by_word.get(word, ()))
            for word in words
        }


AMBIGUOUS_ANALYSES = {
    "காட்டில்": ("காடு+noun+loc", "காடு+noun+abl"),
    "புத்தகத்தில்": ("புத்தகம்+noun+infInc+loc", "புத்தகம்+noun+infInc+soc"),
    "செல்லாமை": (
        "செல்லாமை+noun+nom",
        "செல்+verb+nonfin+sim+neg=ஆ+verbalnoun=மை",
    ),
}


def test_canonical_ambiguity_encoding_preserves_complete_readings():
    readings = (
        ("இந்தியா", "<POS_NOUN>", "<CASE_LOC>"),
        ("இந்தியா", "<POS_NOUN>", "<CASE_ABL>"),
    )

    encoded = encode_readings(readings)

    assert encoded == (
        "இந்தியா",
        "<POS_NOUN>",
        "<READINGS>",
        "<CASE_LOC>",
        "<ALT>",
        "<CASE_ABL>",
    )
    assert decode_readings(encoded) == readings


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_uses_fst_for_known_noun():
    tokenizer = TamilMorphTokenizer(mode="best")
    records = tokenizer.tokenize("மரங்களிலிருந்து")
    assert len(records) == 1
    assert records[0].best_analysis is not None
    assert records[0].tokens[:2] == ("மரம்", "<POS_NOUN>")
    assert "<NUM_PL>" in records[0].tokens
    assert "<CASE_ABL>" in records[0].tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "raw_analysis"),
    [
        ("அகர", "அகரம்+noun+compoundmodifier"),
        ("முதல", "முதல்+pp-particle"),
        ("எழுத்தெல்லாம்", "எழுத்து+noun+nom+all"),
        ("முதற்றே", "முதல்+pp-particle+foc=ஏ"),
    ],
)
def test_thirukkural_first_couplet_surfaces_have_semantic_analyses(
    surface, raw_analysis
):
    record = TamilMorphTokenizer(
        mode="best", use_default_entities=False
    ).tokenize(surface)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == raw_analysis
    assert record.fallback is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "raw_analysis"),
    [
        ("வீடெல்லாம்", "வீடு+noun+nom+all"),
        ("மொட்டெல்லாம்", "மொட்டு+noun+nom+all"),
        ("எழுத்தெல்லாம்", "எழுத்து+noun+nom+all"),
        ("ஆறெல்லாம்", "ஆறு+noun+nom+all"),
    ],
)
def test_short_u_noun_ellaam_classes_are_analyzed_productively(
    surface, raw_analysis
):
    record = TamilMorphTokenizer(
        mode="best", use_default_entities=False
    ).tokenize(surface)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == raw_analysis
    assert "<QUANT_ALL>" in record.tokens
    assert record.fallback is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "raw_analysis"),
    [
        ("ஆல்பத்தில்", "ஆல்பம்+noun+infInc+loc"),
        ("வெப்பமண்டல", "வெப்பமண்டலம்+noun+compoundmodifier"),
        ("ஆரம்பகாலக்", "ஆரம்பகாலம்+noun+compoundmodifier+sandhik=க்"),
        ("பிற்பகுதியில்", "பிற்பகுதி+noun+loc"),
        ("முற்பகுதியிலும்", "முற்பகுதி+noun+loc+add"),
        ("நடுப்பகுதியை", "நடுப்பகுதி+noun+acc"),
        ("பெரும்பகுதியின்", "பெரும்பகுதி+noun+gen"),
        ("தரவரிசையில்", "தரவரிசை+noun+loc"),
        ("இசைக்குழுவின்", "இசைக்குழு+noun+gen"),
        ("படைப்பிரிவுகள்", "படைப்பிரிவு+noun+pl+nom"),
        ("ஸ்டுடியோவில்", "ஸ்டுடியோ+noun+loc"),
        ("கிளப்பின்", "கிளப்+noun+gen"),
        ("சாம்பியன்ஷிப்பை", "சாம்பியன்ஷிப்+noun+acc"),
        ("கிட்டார்", "கிட்டார்+noun+nom"),
        ("விமர்சகர்களிடமிருந்து", "விமர்சகர்+noun+pl+abl"),
        ("மாணவர்களிடமிருந்து", "மாணவர்+noun+pl+abl"),
        ("நண்பர்களிடமிருந்து", "நண்பன்+noun+pl+abl"),
        ("கைதிகளிடமிருந்து", "கைதி+noun+pl+abl"),
        ("இதுவாகும்", "இது+pron+dem+prox+3sgn+trans=ஆக+cop+fut+3sgn"),
        ("அவையாகும்", "அவை+pron+dem+dist+3pln+trans=ஆக+cop+fut+3pln"),
        ("எதுவாக", "எது+pron+inter+3sgn+trans=ஆக"),
    ],
)
def test_translation_training_coverage_repairs_are_semantic(
    surface, raw_analysis
):
    record = TamilMorphTokenizer(
        mode="best", use_default_entities=False
    ).tokenize(surface)[0]

    assert raw_analysis in {analysis.raw for analysis in record.analyses}
    assert record.best_analysis is not None
    assert record.fallback is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "raw_analysis"),
    [
        ("மரமற்ற", "மரம்+noun+privative=அற்ற+adjpart=அ+adj"),
        ("மரமற்றது", "மரம்+noun+privative=அற்ற+adjpart=அ+PartNoun=அது"),
        ("மரங்களான", "மரம்+noun+pl+nom+cop=ஆ+adjpart=ன"),
        ("மரங்களற்ற", "மரம்+noun+pl+privative=அற்ற+adjpart=அ+adj"),
        ("தடையற்ற", "தடை+noun+privative=அற்ற+adjpart=அ+adj"),
        ("அளவற்ற", "அளவு+noun+privative=அற்ற+adjpart=அ+adj"),
        ("முதல்முறையாக", "முதல்முறை+noun+trans=ஆக+adv"),
        ("பிஸியாக", "பிஸி+adj+trans=ஆக+adv"),
        ("மாதந்தோறும்", "மாதம்+noun+time+distrib+adv"),
        ("வீடுதோறும்", "வீடு+noun+distrib+adv"),
    ],
)
def test_productive_modifier_and_reviewed_adverb_coverage_is_semantic(
    surface, raw_analysis
):
    record = TamilMorphTokenizer(
        mode="best", use_default_entities=False
    ).tokenize(surface)[0]

    assert raw_analysis in {analysis.raw for analysis in record.analyses}
    assert record.best_analysis is not None
    assert record.fallback is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "raw_analysis"),
    [
        ("மாசற்ற", "மாசு+noun+privative=அற்ற+adjpart=அ+adj"),
        ("அருகிலுள்ள", "அருகு+noun+loc=இல்+exist+adjpart=அ+adj"),
        ("ஐரோப்பிய", "ஐரோப்பா+noun+adjpart=இய+adj"),
    ],
)
def test_reviewed_noun_modifiers_have_one_owner_and_human_readable_tokens(
    surface, raw_analysis
):
    record = TamilMorphTokenizer(
        mode="best", use_default_entities=False
    ).tokenize(surface)[0]

    matching = {
        (analysis.model, analysis.raw)
        for analysis in record.analyses
        if analysis.raw == raw_analysis
    }
    assert matching == {("noun.fst", raw_analysis)}
    assert "<POS_NOUN>" in record.tokens
    assert record.fallback is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_uses_fst_for_known_verb():
    tokenizer = TamilMorphTokenizer(mode="best")
    records = tokenizer.tokenize("படித்தான்")
    assert len(records) == 1
    assert records[0].best_analysis is not None
    assert records[0].tokens[0] == "படி"
    assert "<POS_VERB>" not in records[0].tokens
    assert "<VERB_FINITE>" not in records[0].tokens
    assert "<TENSE_PAST>" in records[0].tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "lemma", "expected_tokens"),
    [
        (
            "முக்கியமான",
            "முக்கியம்",
            {"<POS_NOUN>", "<CASE_NOM>", "<COPULA>", "<ADJECTIVAL_PARTICIPLE>"},
        ),
        (
            "மக்களுக்கான",
            "மக்கள்",
            {"<POS_NOUN>", "<NUM_PL>", "<CASE_DAT>", "<COPULA>", "<ADJECTIVAL_PARTICIPLE>"},
        ),
        (
            "ஒன்றான",
            "ஒன்று",
            {"<NUM_CARDINAL>", "<COPULA>", "<ADJECTIVAL_PARTICIPLE>"},
        ),
        (
            "இவ்வாறான",
            "இவ்வாறு",
            {"<POS_ADV>", "<COPULA>", "<ADJECTIVAL_PARTICIPLE>"},
        ),
    ],
)
def test_copular_participle_families_preserve_their_base_semantics(
    surface, lemma, expected_tokens
):
    record = TamilMorphTokenizer(mode="best").tokenize(surface)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.lemma == lemma
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_overt_iru_perfect_chain_preserves_all_semantic_signal():
    record = TamilMorphTokenizer(mode="best").tokenize("வைக்கப்பட்டிருந்த")[0]

    assert record.tokens == (
        "வை",
        "<VOICE_PASSIVE>",
        "<ASPECT_PERFECT>",
        "<LINK_VPART>",
        "இரு",
        "<TENSE_PAST>",
        "<ADJECTIVAL_PARTICIPLE>",
    )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_source_attested_complex_verbs_retain_productive_link_semantics():
    tokenizer = TamilMorphTokenizer(mode="best")

    assert tokenizer.tokenize("கற்றுக்கொடுத்தான்")[0].tokens == (
        "கல்",
        "<LINK_VPART>",
        "கொடு",
        "<TENSE_PAST>",
        "<PERSON_3SG_MASC>",
    )
    assert tokenizer.tokenize("அடக்கியிருந்தான்")[0].tokens == (
        "அடக்கு",
        "<ASPECT_PERFECT>",
        "<LINK_VPART>",
        "இரு",
        "<TENSE_PAST>",
        "<PERSON_3SG_MASC>",
    )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_c11_resultative_participle_is_semantically_complete():
    record = TamilMorphTokenizer(mode="best").tokenize("தெரிவித்துள்ள")[0]

    assert record.tokens == (
        "தெரிவி",
        "<ASPECT_PERFECT>",
        "<TENSE_PRESENT>",
        "<ADJECTIVAL_PARTICIPLE>",
    )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["கதை", "அடை", "ஆடவை", "கிறி"])
def test_missing_noun_homograph_batch_preserves_both_pos_readings(word):
    record = TamilMorphTokenizer().tokenize(word)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == f"{word}+noun+nom"
    assert any("+noun+nom" in analysis.raw for analysis in record.analyses)
    assert any("+verb+" in analysis.raw for analysis in record.analyses)
    assert "<POS_NOUN>" in record.tokens
    assert "<VERB_IMPERATIVE>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("ஆறாக", "ஆறு", {"<NUM_CARDINAL>", "<CASE_TRANS>"}),
        ("ஆற்றாக", "ஆறு", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("குறைபாடாக", "குறைபாடு", {"<POS_NOUN>", "<CASE_TRANS>"}),
    ],
)
def test_cardinal_and_noun_translatives_remain_semantically_distinct(
    word, lemma, expected_tokens
):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.lemma == lemma
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("இந்தியாவில்", "இந்தியா", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("செயற்கையில்", "செயற்கை", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("நுண்ணறிவில்", "நுண்ணறிவு", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("உருவாக்குகிறது", "உருவாக்கு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("ஓடியது", "ஓடு", {"<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("உள்ளது", "உள்", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("உள்ளன", "உள்", {"<TENSE_PRESENT>", "<PERSON_3PL_NEUT>"}),
        ("உள்ளார்", "உள்", {"<TENSE_PRESENT>", "<PERSON_3SG_HON>"}),
        ("உள்ளார்கள்", "உள்", {"<TENSE_PRESENT>", "<PERSON_3PL_EPICENE>"}),
        ("செயல்படுவது", "செயல்படு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("தட்டுவது", "தட்டு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("மாற்றுவது", "மாற்று", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("வாங்குவது", "வாங்கு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("கொள்வது", "கொள்", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("பெறுவது", "பெறு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("நகுவது", "நகு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("அணிவதும்", "அணி", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<CLITIC_ADD>"}),
        ("வெளியாவது", "வெளியா", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("வழிபடுவதும்", "வழிபடு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<CLITIC_ADD>"}),
        ("செய்யாமை", "செய்", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("செல்லாமை", "செல்", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("படிக்காமை", "படி", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("அடையாமை", "அடை", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("கூறுகின்றனர்", "கூறு", {"<TENSE_PRESENT>", "<PERSON_3PL_EPICENE>"}),
        ("முற்படுகின்றனர்", "முற்படு", {"<TENSE_PRESENT>", "<PERSON_3PL_EPICENE>"}),
        ("என்கிறார்", "என்", {"<TENSE_PRESENT>", "<PERSON_3SG_HON>"}),
        ("செல்கிறார்", "செல்", {"<TENSE_PRESENT>", "<PERSON_3SG_HON>"}),
        ("உயர்த்தப்பட்டது", "உயர்த்து", {"<VOICE_PASSIVE>", "<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("உயர்த்தப்பட்டுள்ளது", "உயர்த்து", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("தெரிவிக்கப்பட்டுள்ளது", "தெரிவி", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("தொகுக்கப்பட்டுள்ளது", "தொகு", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("பாதிக்கப்பட்டுள்ளது", "பாதி", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("அறிவிக்கின்றன", "அறிவி", {"<TENSE_PRESENT>", "<PERSON_3PL_NEUT>"}),
        ("அறிவித்தோம்", "அறிவி", {"<TENSE_PAST>", "<PERSON_1PL>"}),
        ("அறிவித்தது", "அறிவி", {"<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("அறிவிக்கப்பட்டுள்ளது", "அறிவி", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("விடுவித்தது", "விடுவி", {"<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("தெளிவித்தது", "தெளிவி", {"<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("இசையமைத்துள்ளார்", "இசையமை", {"<ASPECT_PERFECT>", "<PERSON_3SG_HON>"}),
        ("அமைத்துள்ளார்", "அமை", {"<ASPECT_PERFECT>", "<PERSON_3SG_HON>"}),
        ("சமைத்துள்ளது", "சமை", {"<ASPECT_PERFECT>", "<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("அமைப்பது", "அமை", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("சமைப்பதும்", "சமை", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<CLITIC_ADD>"}),
        ("கூறுவது", "கூறு", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("செல்வது", "செல்", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("எழுதுவது", "எழுது", {"<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("அறிவிக்கப்படுவதில்லை", "அறிவி", {"<POS_VERBAL_NOUN>", "<VOICE_PASSIVE>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("வழங்கப்படுவதில்லை", "வழங்கு", {"<POS_VERBAL_NOUN>", "<VOICE_PASSIVE>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("பயன்படுத்தப்படுவதில்லை", "பயன்படுத்து", {"<POS_VERBAL_NOUN>", "<VOICE_PASSIVE>", "<ACTION_NOMINAL>", "<POLARITY_NEG>"}),
        ("அனுமதிக்கப்பட்டுள்ளது", "அனுமதி", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("அழைக்கப்பட்டுள்ளது", "அழை", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("பயன்படுத்தப்பட்டுள்ளது", "பயன்படுத்து", {"<VOICE_PASSIVE>", "<ASPECT_PERFECT>", "<PERSON_3SG_NEUT>"}),
        ("உயர்த்த", "உயர்த்து", {"<VERB_INFINITIVE>"}),
        ("புரிய", "புரி", {"<VERB_INFINITIVE>"}),
        ("அறிய", "அறி", {"<VERB_INFINITIVE>"}),
        ("விரிய", "விரி", {"<VERB_INFINITIVE>"}),
    ],
)
def test_source_backed_fst_coverage_expansions(word, lemma, expected_tokens):
    tokenizer = TamilMorphTokenizer(use_default_entities=False)
    record = tokenizer.tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["எளிதாக்குவதும்"])
def test_residual_verbal_nominal_root_class_gaps_remain_surface_fallbacks(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is None
    assert record.fallback == "unknown_tamil_surface"
    assert record.tokens == (word,)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_productive_auxiliary_verbal_nominal_closes_reviewed_gap():
    record = TamilMorphTokenizer(mode="best").tokenize("தெரிந்துகொள்வது")[0]
    assert record.best_analysis is not None
    assert record.tokens == (
        "தெரி", "<LINK_VPART>", "கொள்", "<POS_VERBAL_NOUN>",
        "<ACTION_NOMINAL>",
    )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma"),
    [
        ("அஃறிணை", "அஃறிணை"),
        ("அகராதி", "அகராதி"),
        ("அமைதி", "அமைதி"),
        ("அரிசி", "அரிசி"),
        ("அரண்மனை", "அரண்மனை"),
        ("அதிகாரி", "அதிகாரி"),
        ("அக்கா", "அக்கா"),
        ("அகப்பா", "அகப்பா"),
    ],
)
def test_source_backed_noun_tranche_examples(word, lemma):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert "<POS_NOUN>" in record.tokens
    assert "<CASE_NOM>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma"),
    [
        ("இறுதி", "இறுதி"),
        ("கிணறு", "கிணறு"),
        ("கடன்", "கடன்"),
        ("பயன்", "பயன்"),
        ("இடையூறு", "இடையூறு"),
        ("பெரியோன்", "பெரியோன்"),
    ],
)
def test_source_backed_noun_tranche_2_examples(word, lemma):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert "<POS_NOUN>" in record.tokens
    assert "<CASE_NOM>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma"),
    [
        ("பெண்களும்", "பெண்"),
        ("ஆண்களும்", "ஆண்"),
        ("மரங்களும்", "மரம்"),
    ],
)
def test_noun_plural_additive_um_forms(word, lemma):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>", "<CLITIC_ADD>"}.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
        [
            ("என", {"<COMPLEMENTIZER>"}),
            ("மட்டும்", {"<POSTPOSITION>", "<PART_ONLY>"}),
            ("இல்லை", {"<COPULA>"}),
            ("ஏன்", {"<POS_ADV>"}),
            ("க்கும்", {"<POSTPOSITION>", "<COMPARATIVE>", "<CLITIC_ADD>"}),
    ],
)
def test_common_function_words_are_fst_backed(word, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
    [
        ("இந்த", {"<DEICTIC>", "<DEICTIC_PROX>"}),
        ("அந்த", {"<DEICTIC>", "<DEICTIC_DIST>"}),
        ("எந்த", {"<DEICTIC>"}),
        ("இப்பொழுது", {"<DEICTIC>", "<DEICTIC_PROX>", "<DEICTIC_TIME>", "<POS_ADV>"}),
        ("அப்பொழுது", {"<DEICTIC>", "<DEICTIC_DIST>", "<DEICTIC_TIME>", "<POS_ADV>"}),
        ("எப்பொழுது", {"<DEICTIC>", "<DEICTIC_INTERROGATIVE>", "<DEICTIC_TIME>", "<POS_ADV>"}),
        ("இந்நிலையில்", {"<DEICTIC>", "<DEICTIC_PROX>", "<DEICTIC_SITUATION>", "<POS_ADV>"}),
        ("இவ்வகை", {"<DEICTIC>", "<DEICTIC_PROX>", "<DEICTIC_TYPE>", "<POS_ADJ>"}),
    ],
)
def test_deictic_function_forms_are_semantically_specific(word, expected_tokens):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    "word",
    [
        "தேர்தல்",
        "பாலம்",
        "சுற்றுலா",
        "நடவடிக்கை",
        "கொள்முதல்",
        "உற்பத்தி",
        "அலுவலர்",
        "உடற்பயிற்சி",
        "நல்லறம்",
        "ஜனாதிபதி",
        "பட்டதாரி",
        "மன்னார்",
        "பேப்பர்",
        "அழுத்தம்",
        "ஓட்டம்",
        "விற்பனை",
        "குறைபாடு",
        "இயக்குநர்",
    ],
)
def test_corpus_backed_common_nouns_are_fst_backed(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    expected = (
        {"<POS_NOUN>", "<CASE_NOM>", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}
        if word == "தேர்தல்"
        else {"<POS_NOUN>", "<CASE_NOM>"}
    )
    assert expected.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("மரமும்", "மரம்", {"<POS_NOUN>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("எண்ணிக்கையும்", "எண்ணிக்கை", {"<POS_NOUN>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("புலியும்", "புலி", {"<POS_NOUN>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("மாணவனும்", "மாணவன்", {"<POS_NOUN>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("மரமாக", "மரம்", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("காரணமாக", "காரணம்", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("இயக்குநராக", "இயக்குநர்", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("எண்ணிக்கையாக", "எண்ணிக்கை", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("காடாக", "காடு", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("குறைபாடாக", "குறைபாடு", {"<POS_NOUN>", "<CASE_TRANS>"}),
        ("பொன்னும்", "பொன்", {"<POS_NOUN>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("பொன்னாக", "பொன்", {"<POS_NOUN>", "<CASE_TRANS>"}),
    ],
)
def test_noun_singular_additive_and_translative_forms_are_fst_backed(word, lemma, expected_tokens):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["சுமார்", "அதனால்"])
def test_corpus_backed_common_adverbs_are_fst_backed(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert "<POS_ADV>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
    [
        ("தங்கள்", {"<POS_PRONOUN>", "<PRON_POSSESSIVE>"}),
        ("ஒருவர்", {"<POS_PRONOUN>", "<SEM_HUMAN>", "<NUM_SG>"}),
        ("அனைவரும்", {"<POS_QUANTIFIER>", "<SEM_HUMAN>", "<QUANT_ALL>", "<CLITIC_ADD>"}),
        ("எல்லா", {"<POS_QUANTIFIER>", "<QUANT_ALL>", "<DETERMINER>"}),
        ("என்ன", {"<POS_PRONOUN>", "<DEICTIC_INTERROGATIVE>"}),
        ("எத்தனை", {"<POS_QUANTIFIER>", "<DEICTIC_INTERROGATIVE>"}),
        ("அதே", {"<DEICTIC>", "<DEICTIC_DIST>", "<DEICTIC_SAME>"}),
        ("அந்தந்த", {"<DEICTIC>", "<DEICTIC_DIST>", "<DISTRIBUTIVE>"}),
        ("இவ்வளவு", {"<DEICTIC>", "<DEICTIC_PROX>", "<DEGREE>"}),
        ("அவ்வளவு", {"<DEICTIC>", "<DEICTIC_DIST>", "<DEGREE>"}),
        ("வேண்டாம்", {"<MODAL>", "<POLARITY_NEG>", "<MOOD_PROHIBITIVE>"}),
        ("உண்டா", {"<EXISTENTIAL>", "<MOOD_QUESTION>"}),
    ],
)
def test_pronoun_quantifier_function_forms_are_semantically_specific(word, expected_tokens):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_etthanai_preserves_noun_quantifier_ambiguity_but_prefers_quantifier():
    record = TamilMorphTokenizer().tokenize("எத்தனை")[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == "எத்தனை+quant+inter"
    assert "எத்தன்+noun+acc" in {analysis.raw for analysis in record.analyses}
    assert "எத்தனை+quant+inter" in {analysis.raw for analysis in record.analyses}
    assert "<POS_NOUN>" in record.tokens
    assert "<CASE_ACC>" in record.tokens
    assert "<POS_QUANTIFIER>" in record.tokens
    assert "<DEICTIC_INTERROGATIVE>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("கலெக்டர்", "கலெக்டர்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("கலெக்டரை", "கலெக்டர்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("வைரஸ்", "வைரஸ்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("வைரஸில்", "வைரஸ்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("குக்கர்", "குக்கர்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("டீ", "டீ", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("டீயை", "டீ", {"<POS_NOUN>", "<CASE_ACC>"}),
    ],
)
def test_selective_loanword_nouns_are_fst_backed(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["பி", "ஜி", "டி", "எஸ்"])
def test_selective_single_letter_abbreviations_are_fst_backed(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert {"<ABBREVIATION>", "<LETTER_NAME>"}.issubset(record.tokens)


def test_numeric_ordinal_is_one_structured_semantic_span():
    record = TamilMorphTokenizer().tokenize("18ம்")[0]
    assert record.surface == "18ம்"
    assert record.tokens == ("18", "<NUM_ORDINAL>")
    assert record.fallback == "numeric_ordinal"


def test_numeric_case_suffix_is_one_structured_semantic_span():
    tokenizer = TamilMorphTokenizer()
    record = tokenizer.tokenize("1993ல்")[0]

    assert record.surface == "1993ல்"
    assert record.tokens == ("1993", "<CASE_LOC>")
    assert record.fallback == "numeric_case"


def test_single_tamil_word_with_period_is_split_from_punctuation():
    tokenizer = TamilMorphTokenizer()

    assert tokenizer.split_words("இ.") == ["இ", "."]


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_sentence_final_tamil_word_is_not_an_abbreviation():
    tokenizer = TamilMorphTokenizer()
    records = tokenizer.tokenize("அவன் வந்தான். மு.க. ராமன் பேசினார்.")

    assert [record.surface for record in records] == [
        "அவன்", "வந்தான்", ".", "மு.க.", "ராமன்", "பேசினார்", ".",
    ]
    assert records[1].fallback != "dotted_abbreviation"
    assert records[3].fallback == "dotted_abbreviation"
    assert records[5].fallback != "dotted_abbreviation"


def test_informal_vocative_before_period_is_not_an_abbreviation():
    tokenizer = TamilMorphTokenizer()

    assert tokenizer.split_words("விட்டுடு பா.") == ["விட்டுடு", "பா", "."]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("என்ன?!", ["என்ன", "?", "!"]),
        ("வா...", ["வா", ".", ".", "."]),
        ('“தமிழ்,” என்றார்.', ["“", "தமிழ்", ",", "”", "என்றார்", "."]),
        ("தமிழ்—மொழி", ["தமிழ்", "—", "மொழி"]),
        ("விலை 3.14.", ["விலை", "3.14", "."]),
        ("1,23,456 பேர்", ["1,23,456", "பேர்"]),
        ("தி.மு.க.,", ["தி.மு.க.", ","]),
        ("மு.க. வந்தார்.", ["மு.க.", "வந்தார்", "."]),
    ],
)
def test_punctuation_and_structured_form_boundaries(text, expected):
    assert TamilMorphTokenizer().split_words(text) == expected


def test_only_multi_segment_dotted_tamil_forms_are_surface_abbreviations():
    tokenizer = TamilMorphTokenizer()

    single = tokenizer.tokenize("பா.")
    dotted = tokenizer.tokenize("மு.க.")

    assert [record.surface for record in single] == ["பா", "."]
    assert all(record.fallback != "dotted_abbreviation" for record in single)
    assert len(dotted) == 1
    assert dotted[0].fallback == "dotted_abbreviation"
    assert "<ABBREVIATION>" in dotted[0].tokens


@pytest.mark.parametrize("mark", [".", ",", "?", "!", ":", ";", "…", "—", "“", "”"])
def test_punctuation_is_intentional_byte_encoding_not_a_surface_fallback(mark):
    record = TamilMorphTokenizer().tokenize(mark)[0]

    assert record.surface == mark
    assert record.tokens == (mark,)
    assert record.fallback == "punctuation"


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_terminal_aytham_delimiter_does_not_absorb_the_lexical_word():
    tokenizer = TamilMorphTokenizer()
    records = tokenizer.tokenize("பெயர்ஃ")

    assert [record.surface for record in records] == ["பெயர்", "ஃ"]
    assert records[0].best_analysis is not None
    assert records[1].fallback == "surface"


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_internal_aytham_remains_part_of_a_tamil_word():
    tokenizer = TamilMorphTokenizer()
    records = tokenizer.tokenize("அஃது")

    assert [record.surface for record in records] == ["அஃது"]


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_dotted_and_hyphenated_entity_abbreviations_preserve_semantics():
    tokenizer = TamilMorphTokenizer(mode="best")
    dotted = tokenizer.tokenize("தி.மு.க")[0]
    assert dotted.tokens == ("திமுக", "<ENTITY_ORG>", "<CASE_NOM>")
    assert dotted.fallback == "orthographic_entity_variant"

    hyphenated = tokenizer.tokenize("திமுக-வுக்கு")[0]
    assert hyphenated.tokens == ("திமுக", "<ENTITY_ORG>", "<CASE_DAT>")
    assert hyphenated.fallback == "orthographic_entity_variant"


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("ஜூஸ்", "ஜூஸ்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("கேக்கை", "கேக்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("பிஸ்கட்டை", "பிஸ்கட்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("சாக்லேட்டில்", "சாக்லேட்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("மார்ச்சில்", "மார்ச்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("ஆகஸ்டில்", "ஆகஸ்ட்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("பெங்களூரு", "பெங்களூரு", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("ஹைதராபாத்தில்", "ஹைதராபாத்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("டிக்கெட்டை", "டிக்கெட்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("பைக்கில்", "பைக்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("மொபைல்", "மொபைல்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("வீடியோவை", "வீடியோ", {"<POS_NOUN>", "<CASE_ACC>"}),
    ],
)
def test_calendar_place_and_common_loan_nouns_are_fst_backed(word, lemma, expected_tokens):
    record = TamilMorphTokenizer(use_default_entities=False).tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    "word",
    ["தமிழக", "ஐக்கிய", "மாவட்ட", "தேசிய", "பிரபல", "சரியான", "தேசியக்", "நீர்வாழ்", "துடுப்பாட்ட"],
)
def test_corpus_backed_adjectival_stems_are_fst_backed(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert "<POS_ADJ>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["கடுமையாக", "குறைவாக", "வலுவின்றி"])
def test_corpus_backed_adverbial_stems_are_fst_backed(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert "<POS_ADV>" in record.tokens or "<POS_ADV>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
    [
        ("என்பதை", {"<COMPLEMENTIZER>", "<CASE_ACC>"}),
        ("எனக்", {"<COMPLEMENTIZER>", "<SANDHI_K>"}),
    ],
)
def test_complementizer_case_forms_are_fst_backed(word, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("பேசிய", "பேசு", {"<TENSE_PAST>"}),
        ("வருகின்ற", "வா", {"<TENSE_PRESENT>"}),
        ("வருகிற", "வா", {"<TENSE_PRESENT>", "<ADJECTIVAL_PARTICIPLE>"}),
        ("என்கிற", "என்", {"<TENSE_PRESENT>", "<ADJECTIVAL_PARTICIPLE>"}),
        ("இருக்கிற", "இரு", {"<TENSE_PRESENT>", "<ADJECTIVAL_PARTICIPLE>"}),
        ("படிக்கிற", "படி", {"<TENSE_PRESENT>", "<ADJECTIVAL_PARTICIPLE>"}),
        (
            "செய்யப்படுகிற",
            "செய்",
            {"<VOICE_PASSIVE>", "<TENSE_PRESENT>", "<ADJECTIVAL_PARTICIPLE>"},
        ),
        ("என்றார்", "என்", {"<TENSE_PAST>"}),
        ("ஆவார்", "ஆகு", {"<TENSE_FUTURE>"}),
        ("விமர்சித்து", "விமர்சி", {"<VERBAL_PARTICIPLE>"}),
        ("வந்தார்", "வா", {"<TENSE_PAST>", "<PERSON_3SG_HON>"}),
        ("வந்தனர்", "வா", {"<TENSE_PAST>", "<PERSON_3PL_EPICENE>"}),
        ("வருகிறார்", "வா", {"<TENSE_PRESENT>", "<PERSON_3SG_HON>"}),
        ("வருகின்றன", "வா", {"<TENSE_PRESENT>", "<PERSON_3PL_NEUT>"}),
        ("வருவார்", "வா", {"<TENSE_FUTURE>", "<PERSON_3SG_HON>"}),
        ("உள்ளனர்", "உள்", {"<TENSE_PRESENT>", "<PERSON_3PL_EPICENE>"}),
        ("பணியாற்றினார்", "பணியாற்று", {"<TENSE_PAST>", "<PERSON_3SG_HON>"}),
        ("பயன்படுத்தினார்", "பயன்படுத்து", {"<TENSE_PAST>", "<PERSON_3SG_HON>"}),
        ("பயன்படுத்தப்படுகிறது", "பயன்படுத்து", {"<VOICE_PASSIVE>", "<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("செயல்பட்டு", "செயல்படு", {"<VERBAL_PARTICIPLE>"}),
        ("உயிரிழந்தனர்", "உயிரிழ", {"<TENSE_PAST>", "<PERSON_3PL_EPICENE>"}),
        ("தெரிய", "தெரி", {"<VERB_INFINITIVE>"}),
        (
            "நடிக்க",
            "நடி",
            {"<VERB_INFINITIVE>", "<MOOD_OPTATIVE>"},
        ),
        ("கொள்ள", "கொள்", {"<VERB_INFINITIVE>"}),
        ("சொன்ன", "சொல்லு", {"<TENSE_PAST>", "<ADJECTIVAL_PARTICIPLE>"}),
        ("ஏற்பட்டுள்ளது", "ஏற்படு", {"<ASPECT_PERFECT>", "<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("வந்துள்ளது", "வா", {"<ASPECT_PERFECT>", "<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("தெரிவித்துள்ளார்", "தெரிவி", {"<ASPECT_PERFECT>", "<TENSE_PRESENT>", "<PERSON_3SG_HON>"}),
        ("அனுப்பப்பட்டனர்", "அனுப்பு", {"<VOICE_PASSIVE>", "<TENSE_PAST>", "<PERSON_3PL_EPICENE>"}),
    ],
)
def test_modern_verb_derived_forms_are_fst_backed(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(("word", "lemma"), [("விழும்", "விழு"), ("எழும்", "எழு")])
def test_c4_u_final_future_forms_are_fst_backed(word, lemma):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert {
        "<TENSE_FUTURE>",
        "<FUTURE_ADJECTIVAL_PARTICIPLE>",
    }.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("நம்பிக்கை", "நம்பிக்கை", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("நம்பிக்கையை", "நம்பிக்கை", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("நம்பிக்கையில்", "நம்பிக்கை", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("திருநம்பி", "திருநம்பி", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("திருநம்பியை", "திருநம்பி", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("நம்பி", "நம்பி", {"<POS_NOUN>", "<CASE_NOM>"}),
    ],
)
def test_noun_pronoun_rewrite_fix_preserves_nambi_roots(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("உதவுகிறது", "உதவு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("தூங்குகிறது", "தூங்கு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("திரும்பியது", "திரும்பு", {"<TENSE_PAST>", "<PERSON_3SG_NEUT>"}),
        ("காப்பாற்றுகிறது", "காப்பாற்று", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("பயன்படுகிறது", "பயன்படு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
    ],
)
def test_source_backed_c5_verb_tranche_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("பொறுக்கிறது", "பொறு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("வெறுகிறது", "வெறு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("உண்டாக்குகிறது", "உண்டாக்கு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("பயப்படுகிறது", "பயப்படு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("மேம்படுகிறது", "மேம்படு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
        ("களிகூறுகிறது", "களிகூறு", {"<TENSE_PRESENT>", "<PERSON_3SG_NEUT>"}),
    ],
)
def test_source_backed_c5_verb_tranche_2_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("சீனாவில்", "சீனா", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("சீதையை", "சீதை", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("தமிழ்நாட்டில்", "தமிழ்நாடு", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("ஜப்பானில்", "ஜப்பான்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("கேரளத்தில்", "கேரளம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_LOC>"}),
        ("பிள்ளையாருக்கு", "பிள்ளையார்", {"<POS_NOUN>", "<CASE_DAT>"}),
        ("நபிமார்கள்", "நபி", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>"}),
        ("இறைத்தூதர்கள்", "இறைத்தூதர்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>"}),
        ("இவ்வசனங்கள்", "இவ்வசனம்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>"}),
        ("ஊராட்சித்", "ஊராட்சி", {"<POS_NOUN>", "<CASE_NOM>", "<SANDHI_T>"}),
        ("கிராமப்புறங்களில்", "கிராமப்புறம்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("பிரதானமாக", "பிரதானம்", {"<POS_NOUN>", "<CASE_TRANS>"}),
    ],
)
def test_source_backed_name_tranche_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer(
        mode="best" if "<CASE_TRANS>" in expected_tokens else "compact_ambiguity",
        use_default_entities=False,
    ).tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("பரங்கிப்பேட்டை", "பரங்கிப்பேட்டை", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("சுல்தான்", "சுல்தான்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("ராமநாதபுரத்தில்", "ராமநாதபுரம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_LOC>"}),
        ("உப்பள", "உப்பள", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("திருப்புல்லாணி", "திருப்புல்லாணி", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("இங்கிலாந்து", "இங்கிலாந்து", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("நகரில்", "நகர்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("சின்னத்தை", "சின்னம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_ACC>"}),
        ("கெடிமேடு", "கெடிமேடு", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("எடை", "எடை", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("தாக்குதலுக்கு", "தாக்குதல்", {"<POS_NOUN>", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>", "<CASE_DAT>"}),
        ("நிறுவனர்", "நிறுவனர்", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("தாக்கல்", "தாக்கல்", {"<POS_NOUN>", "<CASE_NOM>", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("வழங்கல்", "வழங்கல்", {"<POS_NOUN>", "<CASE_NOM>", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"}),
        ("ஜல்லிக்கட்டு", "ஜல்லிக்கட்டு", {"<POS_NOUN>", "<CASE_NOM>"}),
    ],
)
def test_corpus_backed_noun_gap_tranche_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
    [
        ("அதனால்தான்", {"<POS_ADV>", "<DEICTIC>", "<DEICTIC_DIST>", "<CLITIC_FOCUS>"}),
        ("இதனால்தான்", {"<POS_ADV>", "<DEICTIC>", "<DEICTIC_PROX>", "<CLITIC_FOCUS>"}),
        ("எதனால்தான்", {"<POS_ADV>", "<DEICTIC>", "<DEICTIC_INTERROGATIVE>", "<CLITIC_FOCUS>"}),
        ("ஏதேனும்", {"<POS_QUANTIFIER>", "<INDEFINITE>", "<CLITIC_ADD>"}),
        ("ஏதாவது", {"<POS_QUANTIFIER>", "<INDEFINITE>"}),
        ("என்பதற்கு", {"<COMPLEMENTIZER>", "<CASE_DAT>"}),
        ("என்பதில்", {"<COMPLEMENTIZER>", "<CASE_LOC>"}),
        ("என்பதால்", {"<COMPLEMENTIZER>", "<CASE_INST>"}),
        ("என்பதன்", {"<COMPLEMENTIZER>", "<CASE_GEN>"}),
        ("என்பதும்", {"<COMPLEMENTIZER>", "<CLITIC_ADD>"}),
        ("எனச்", {"<COMPLEMENTIZER>", "<SANDHI_C>"}),
        ("எனத்", {"<COMPLEMENTIZER>", "<SANDHI_T>"}),
    ],
)
def test_corpus_backed_function_gap_tranche_examples(word, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("உள்ளடக்கங்களை", "உள்ளடக்கம்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>"}),
        ("ஓலை", "ஓலை", {"<POS_NOUN>", "<CASE_NOM>"}),
        ("பத்திரிகைகளும்", "பத்திரிகை", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("புழக்கத்தில்", "புழக்கம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_LOC>"}),
        ("சந்தேகத்திற்கு", "சந்தேகம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_DAT>"}),
        ("மட்டத்திற்கு", "மட்டம்", {"<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_DAT>"}),
        ("நெறிமுறைகளை", "நெறிமுறை", {"<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>"}),
        ("வழித்தடங்களும்", "வழித்தடம்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>", "<CLITIC_ADD>"}),
        ("விமர்சனங்களும்", "விமர்சனம்", {"<POS_NOUN>", "<NUM_PL>", "<CASE_NOM>", "<CLITIC_ADD>"}),
    ],
)
def test_triaged_common_noun_coverage_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.fallback is None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("பாரிஸை", "பாரிஸ்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("பாரிஸில்", "பாரிஸ்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("லடாகை", "லடாக்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("லடாகில்", "லடாக்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("மத்ரித்தை", "மத்ரித்", {"<POS_NOUN>", "<CASE_ACC>"}),
        ("மத்ரித்தில்", "மத்ரித்", {"<POS_NOUN>", "<CASE_LOC>", "<CASE_ABL>"}),
        ("மத்ரித்தால்", "மத்ரித்", {"<POS_NOUN>", "<CASE_INST>"}),
        ("மத்ரித்துக்கு", "மத்ரித்", {"<POS_NOUN>", "<CASE_DAT>"}),
        ("மத்ரித்துடன்", "மத்ரித்", {"<POS_NOUN>", "<CASE_SOC>"}),
        ("மத்ரித்துடைய", "மத்ரித்", {"<POS_NOUN>", "<CASE_GEN>"}),
    ],
)
def test_foreign_final_name_template_examples(word, lemma, expected_tokens):
    record = TamilMorphTokenizer(use_default_entities=False).tokenize(word)[0]
    assert record.best_analysis is not None
    assert lemma in record.tokens
    assert expected_tokens.issubset(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_undu_preserves_eating_and_existential_analyses():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("உண்டு")[0]
    assert record.best_analysis is not None
    assert record.best_analysis.raw == "உள்+verb+fin+sim+strong+pres=∅+3sgn=அது"
    assert {
        "உள்+verb+fin+sim+strong+pres=∅+3sgn=அது",
        "உண்+verb+nonfin+sim+vpart=உ",
    }.issubset({analysis.raw for analysis in record.analyses})
    assert record.ambiguous


def test_unknown_tamil_surface_fallback_without_fst_analysis():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(analyzer=EmptyAnalyzer(), use_default_entities=False)
    records = tokenizer.tokenize("தமிழ்")
    assert records[0].fallback == "unknown_tamil_surface"
    assert records[0].tokens == ("தமிழ்",)


def test_grapheme_fallback_mode_without_fst_analysis():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(
        analyzer=EmptyAnalyzer(),
        unknown_tamil_fallback="grapheme",
    )
    records = tokenizer.tokenize("அரவிந்த்")
    assert records[0].fallback == "grapheme"
    assert records[0].tokens == ("அ", "ர", "வி", "ந்", "த்")


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_handles_maanavanai():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("மாணவனை")[0]
    assert record.best_analysis is not None
    assert record.tokens == ("மாணவன்", "<POS_NOUN>", "<CASE_ACC>")
    assert record.token_count == 3
    assert not record.ambiguous


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_handles_marangalai():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("மரங்களை")[0]
    assert record.best_analysis is not None
    assert record.tokens == ("மரம்", "<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>")
    assert record.token_count == 4
    assert not record.ambiguous


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_preserves_kaattil_ambiguity():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("காட்டில்")[0]
    assert record.best_analysis is not None
    assert record.tokens[0] == "காடு"
    assert "<CASE_LOC>" in record.tokens
    assert record.ambiguous
    assert {analysis.raw for analysis in record.analyses} == {
        "காடு+noun+loc",
        "காடு+noun+abl",
    }


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tokenizer_rejects_false_puthakathil_sociative_ambiguity():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("புத்தகத்தில்")[0]
    assert record.best_analysis is not None
    assert record.tokens[0] == "புத்தகம்"
    assert "<CASE_LOC>" in record.tokens
    assert not record.ambiguous
    assert {analysis.raw for analysis in record.analyses} == {
        "புத்தகம்+noun+infInc+loc",
    }


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_token"),
    [
        ("நேருக்கு-நேர்", "நேருக்கு-நேர்", "<POS_ADV>"),
        ("அக்கடா-என்று", "அக்கடா-என்று", "<POS_ADV>"),
        ("பகுதி-நேர", "பகுதி-நேர", "<POS_ADJ>"),
        ("விலை-உயர்ந்த", "விலை-உயர்ந்த", "<POS_ADJ>"),
    ],
)
def test_hyphenated_fst_lexemes_remain_single_tamil_spans(word, lemma, expected_token):
    tokenizer = TamilMorphTokenizer(mode="best")

    assert tokenizer.split_words(word) == [word]
    assert is_tamil_word(word)
    record = tokenizer.tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.best_analysis.lemma == lemma
    assert expected_token in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_all_audited_hyphenated_fst_lexemes_are_runtime_reachable():
    fixture = Path(__file__).parent / "fixtures" / "hyphenated_fst_lexemes.txt"
    words = [line for line in fixture.read_text(encoding="utf-8").splitlines() if line]
    tokenizer = TamilMorphTokenizer(mode="best")

    assert len(words) == 154
    assert all(tokenizer.split_words(word) == [word] for word in words)
    assert all(is_tamil_word(word) for word in words)
    analyses = tokenizer.analyzer.analyze(words)
    missing = [word for word in words if not analyses.get(word)]
    assert missing == []


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("காட்டில்", ("காடு", "<POS_NOUN>", "<CASE_LOC>")),
        ("புத்தகத்தில்", ("புத்தகம்", "<POS_NOUN>", "<STEM_OBLIQUE>", "<CASE_LOC>")),
    ],
)
def test_best_mode_chooses_one_analysis_for_ambiguous_nouns(word, expected):
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(AMBIGUOUS_ANALYSES),
        mode="best",
    )
    record = tokenizer.tokenize(word)[0]
    assert record.tokens == expected
    assert record.ambiguous


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        (
            "காட்டில்",
            ("காடு", "<POS_NOUN>", "<READINGS>", "<CASE_LOC>", "<ALT>", "<CASE_ABL>"),
        ),
        (
            "புத்தகத்தில்",
            (
                "புத்தகம்",
                "<POS_NOUN>",
                "<STEM_OBLIQUE>",
                "<READINGS>",
                "<CASE_LOC>",
                "<ALT>",
                "<CASE_SOC>",
            ),
        ),
    ],
)
def test_compact_ambiguity_mode_preserves_grouped_case_readings(word, expected):
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(AMBIGUOUS_ANALYSES),
        mode="compact_ambiguity",
    )
    record = tokenizer.tokenize(word)[0]
    assert record.tokens == expected
    assert record.ambiguous


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        (
            "காட்டில்",
            (
                "<READINGS>",
                "காடு",
                "<POS_NOUN>",
                "<CASE_LOC>",
                "<ALT>",
                "காடு",
                "<POS_NOUN>",
                "<CASE_ABL>",
            ),
        ),
        (
            "புத்தகத்தில்",
            (
                "<READINGS>",
                "புத்தகம்",
                "<POS_NOUN>",
                "<STEM_OBLIQUE>",
                "<CASE_LOC>",
                "<ALT>",
                "புத்தகம்",
                "<POS_NOUN>",
                "<STEM_OBLIQUE>",
                "<CASE_SOC>",
            ),
        ),
    ],
)
def test_all_analyses_mode_emits_canonical_reading_groups(word, expected):
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(AMBIGUOUS_ANALYSES),
        mode="all_analyses",
    )
    record = tokenizer.tokenize(word)[0]
    assert record.tokens == expected
    assert record.ambiguous


def test_compact_ambiguity_keeps_each_lemma_associated_with_its_semantics():
    tokenizer = TamilMorphTokenizer(
        analyzer=StaticAnalyzer(AMBIGUOUS_ANALYSES),
        mode="compact_ambiguity",
    )
    record = tokenizer.tokenize("செல்லாமை")[0]

    assert record.surface == "செல்லாமை"
    assert record.tokens == (
        "<READINGS>",
        "செல்",
        "<POLARITY_NEG>",
        "<POS_VERBAL_NOUN>",
        "<ACTION_NOMINAL>",
        "<ALT>",
        "செல்லாமை",
        "<POS_NOUN>",
        "<CASE_NOM>",
    )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("surface", "lemma", "required_tokens"),
    [
        ("சோதிக்காதே", "சோதி", {"<VERB_IMPERATIVE>", "<POLARITY_NEG>"}),
        ("விட்டுடு", "விடு", {"<LINK_VPART>", "<VERB_IMPERATIVE>", "<REGISTER_COLLOQUIAL>"}),
        ("பண்ணுறார்", "பண்ணு", {"<TENSE_PRESENT>", "<PERSON_3SG_HON>", "<REGISTER_COLLOQUIAL>"}),
        ("போனவன்", "போ", {"<TENSE_PAST>", "<POS_PARTICIPIAL_NOUN>", "<PERSON_3SG_MASC>"}),
        ("சென்றவன்", "செல்", {"<TENSE_PAST>", "<POS_PARTICIPIAL_NOUN>", "<PERSON_3SG_MASC>"}),
        ("பார்த்தீங்களா", "பார்", {"<PERSON_2PL>", "<MOOD_QUESTION>", "<REGISTER_COLLOQUIAL>"}),
        ("வந்தாங்களா", "வா", {"<PERSON_3PL_EPICENE>", "<MOOD_QUESTION>", "<REGISTER_COLLOQUIAL>"}),
        ("படிச்சு", "படி", {"<VERBAL_PARTICIPLE>", "<REGISTER_COLLOQUIAL>"}),
        ("படிச்சியா", "படி", {"<PERSON_2SG>", "<MOOD_QUESTION>", "<REGISTER_COLLOQUIAL>"}),
        ("பாரு", "பார்", {"<VERB_IMPERATIVE>", "<PERSON_2SG>", "<REGISTER_COLLOQUIAL>"}),
    ],
)
def test_reviewed_colloquial_and_participial_coverage(surface, lemma, required_tokens):
    record = TamilMorphTokenizer(mode="best").tokenize(surface)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.lemma == lemma
    assert required_tokens <= set(record.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_reviewed_lexical_ranking_and_colloquial_ambiguity():
    tokenizer = TamilMorphTokenizer()

    romba = tokenizer.tokenize("ரொம்ப")[0]
    assert romba.best_analysis is not None
    assert romba.best_analysis.lemma == "ரொம்ப"
    assert "<INTENSIFIER>" in romba.tokens

    paa = tokenizer.tokenize("பா.")
    assert [record.surface for record in paa] == ["பா", "."]
    assert paa[0].best_analysis is not None
    assert {"intj", "voc", "colloq"} <= set(paa[0].best_analysis.tags)

    senju = tokenizer.tokenize("செஞ்சு")[0]
    assert senju.best_analysis is not None
    assert senju.best_analysis.lemma == "செய்"
    assert {"<VERBAL_PARTICIPLE>", "<REGISTER_COLLOQUIAL>"} <= set(senju.tokens)

    senjaa = tokenizer.tokenize("செஞ்சா")[0]
    raw = {analysis.raw for analysis in senjaa.analyses}
    assert any("3sgf" in analysis and "+colloq" in analysis for analysis in raw)
    assert any("+ques=ஆ+colloq" in analysis for analysis in raw)
    assert any("+con=ஆல்+colloq" in analysis for analysis in raw)


def test_special_postposition_prevents_grapheme_fallback():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(analyzer=EmptyAnalyzer())
    record = tokenizer.tokenize("க்குள்")[0]
    assert record.tokens == ("<POST_WITHIN_BY>",)
    assert record.fallback == "special"
    assert record.semantic_special == "<POST_WITHIN_BY>"
    assert record.special_handling == "fallback_override"


def test_mixed_tamil_english_query_keeps_non_tamil_surface_tokens():
    class RecordingAnalyzer:
        def __init__(self):
            self.words = None

        def analyze(self, words):
            self.words = words
            return {word: () for word in words}

    analyzer = RecordingAnalyzer()
    tokenizer = TamilMorphTokenizer(analyzer=analyzer)
    records = tokenizer.tokenize("இந்த EB bill la due date எப்போது?")

    assert [record.surface for record in records] == [
        "இந்த",
        "EB",
        "bill",
        "la",
        "due",
        "date",
        "எப்போது",
        "?",
    ]
    assert analyzer.words == ["இந்த", "எப்போது"]
    assert records[0].fallback == "unknown_tamil_surface"
    assert records[1].tokens == ("EB",)
    assert records[1].fallback == "surface"
    assert records[-1].tokens == ("?",)
    assert records[-1].fallback == "punctuation"

    table = tokenizer.token_table("இந்த EB bill la due date எப்போது?")
    assert table[1]["surface"] == "EB"
    assert table[1]["token_count"] == 1
    assert table[1]["fallback"] == "surface"


def test_unknown_tamil_name_preserves_surface_without_name_heuristic():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(analyzer=EmptyAnalyzer())
    records = tokenizer.tokenize("அரவிந்த் Zoho-வில் வேலை பார்க்கிறார்.")
    record = records[0]
    assert record.surface == "அரவிந்த்"
    assert record.tokens == ("அரவிந்த்",)
    assert record.fallback == "unknown_tamil_surface"
    assert record.special_handling is None


def test_suffix_heuristic_for_unknown_tamil_case_forms():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(
        analyzer=EmptyAnalyzer(), use_default_entities=False
    )
    assert tokenizer.tokenize("இந்தியாவை")[0].tokens == ("இந்தியா", "<CASE_ACC>")
    assert tokenizer.tokenize("இந்தியாவை")[0].fallback == "suffix_heuristic"
    assert tokenizer.tokenize("இந்தியாவில்")[0].tokens == ("இந்தியா", "<CASE_LOC>")
    assert tokenizer.tokenize("இந்தியாவில்")[0].fallback == "suffix_heuristic"
    assert tokenizer.tokenize("இந்தியாவுக்கு")[0].tokens == ("இந்தியா", "<CASE_DAT>")
    assert tokenizer.tokenize("இந்தியாவுக்கு")[0].fallback == "suffix_heuristic"


def test_suffix_heuristic_recovers_u_base_for_vil_forms():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(analyzer=EmptyAnalyzer())
    assert tokenizer.tokenize("உலகளவில்")[0].tokens == ("உலகளவு", "<CASE_LOC>")
    assert tokenizer.tokenize("அளவில்")[0].tokens == ("அளவு", "<CASE_LOC>")


def test_suffix_heuristic_rejects_short_vil_false_positive():
    class EmptyAnalyzer:
        def analyze(self, words):
            return {word: () for word in words}

    tokenizer = TamilMorphTokenizer(analyzer=EmptyAnalyzer())
    record = tokenizer.tokenize("சிவில்")[0]
    assert record.tokens == ("சிவில்",)
    assert record.fallback == "unknown_tamil_surface"


def test_is_tamil_word_distinguishes_scripts():
    assert is_tamil_word("மரங்களை")
    assert not is_tamil_word("EB")
    assert not is_tamil_word("due")
    assert not is_tamil_word("?")


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "alternate_pos"),
    [
        ("அம்மி", "verb"),
        ("அண்டை", "adj"),
        ("நிழல்", "verb"),
        ("பட்டு", "verb"),
        ("சாறு", "verb"),
        ("திருட்டு", "adj"),
        ("கொஞ்சம்", "adv"),
        ("வட்டம்", "adj"),
    ],
)
def test_residual_noun_homographs_preserve_ambiguity_and_rank_noun(word, alternate_pos):
    record = TamilMorphTokenizer().tokenize(word)[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == f"{word}+noun+nom"
    assert any("noun" in analysis.tags for analysis in record.analyses)
    assert any(alternate_pos in analysis.tags for analysis in record.analyses)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["இலங்குதல்", "மென்னுதல்"])
def test_verb_only_citation_forms_emit_only_action_nominal_readings(word):
    record = TamilMorphTokenizer().tokenize(word)[0]

    assert not any("noun" in analysis.tags for analysis in record.analyses)
    assert any("verbalnoun=தல்" in analysis.tags for analysis in record.analyses)
    assert "<POS_VERBAL_NOUN>" in record.tokens
    assert "<ACTION_NOMINAL>" in record.tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_lexicalized_neythal_preserves_noun_and_action_nominal_readings():
    record = TamilMorphTokenizer().tokenize("நெய்தல்")[0]

    assert any("noun" in analysis.tags for analysis in record.analyses)
    assert any("verbalnoun=தல்" in analysis.tags for analysis in record.analyses)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "lemma", "expected_tokens"),
    [
        ("எவ்வளவு", "எவ்வளவு", {"<POS_QUANTIFIER>", "<DEICTIC_INTERROGATIVE>", "<DEGREE>"}),
        ("இத்தனை", "இத்தனை", {"<POS_QUANTIFIER>", "<DEICTIC_PROX>", "<DEGREE>"}),
        ("அத்தனை", "அத்தனை", {"<POS_QUANTIFIER>", "<DEICTIC_DIST>", "<DEGREE>"}),
        ("யாரும்", "யார்", {"<POS_PRONOUN>", "<SEM_HUMAN>", "<CLITIC_ADD>"}),
        ("எதுவும்", "எது", {"<POS_PRONOUN>", "<PERSON_3SG_NEUT>", "<CLITIC_ADD>"}),
        ("ஏதோ", "எது", {"<POS_PRONOUN>", "<PERSON_3SG_NEUT>", "<INDEFINITE>"}),
    ],
)
def test_interrogative_quantifier_families_have_closed_class_semantics(
    word, lemma, expected_tokens
):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert record.best_analysis.lemma == lemma
    assert expected_tokens.issubset(record.best_analysis.morph_tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize("word", ["மரமெல்லாம்", "மரங்களெல்லாம்", "காலெல்லாம்", "பொருளெல்லாம்"])
def test_productive_noun_ellaam_has_quantifier_semantics(word):
    record = TamilMorphTokenizer().tokenize(word)[0]
    assert record.best_analysis is not None
    assert "<QUANT_ALL>" in record.best_analysis.morph_tokens


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
@pytest.mark.parametrize(
    ("word", "expected_tokens"),
    [
        ("இருந்தார்", ("இரு", "<TENSE_PAST>", "<PERSON_3SG_HON>")),
        ("சொன்னார்", ("சொல்", "<TENSE_PAST>", "<PERSON_3SG_HON>")),
        ("ஒன்றில்", ("ஒன்று", "<NUM_CARDINAL>", "<CASE_LOC>")),
        (
            "ஒன்றாகும்",
            (
                "ஒன்று",
                "<NUM_CARDINAL>",
                "<CASE_TRANS>",
                "<COPULA>",
                "<TENSE_FUTURE>",
                "<PERSON_3SG_NEUT>",
            ),
        ),
    ],
)
def test_final_irregular_and_cardinal_repairs_have_semantic_outputs(
    word, expected_tokens
):
    record = TamilMorphTokenizer(mode="best").tokenize(word)[0]

    assert record.tokens == expected_tokens
    assert record.fallback is None


def test_pronoun_semantics_deduplicate_deictic_and_canonicalize_tag_order():
    tokenizer = TamilMorphTokenizer(mode="compact_ambiguity")

    feminine = tokenizer.tokenize("அவள்")[0]
    assert feminine.tokens.count("<DEICTIC>") == 1

    genitive = tokenizer.tokenize("இவர்களுடைய")[0]
    assert len(genitive.analyses) == 2
    assert genitive.tokens == (
        "இவர்கள்",
        "<POS_PRONOUN>",
        "<DEICTIC>",
        "<DEICTIC_PROX>",
        "<PERSON_3PL>",
        "<CASE_GEN>",
    )


def test_isolated_instrumental_noun_outranks_homographic_conditional():
    tokenizer = TamilMorphTokenizer(mode="best")
    record = tokenizer.tokenize("மரத்தால்")[0]

    assert record.best_analysis is not None
    assert record.best_analysis.raw == "மரம்+noun+infInc+inst"
    assert any("+verb+" in analysis.raw for analysis in record.analyses)


def test_inclusive_oblique_possessives_are_productive_runtime_genitives():
    tokenizer = TamilMorphTokenizer(mode="best")

    for surface, lemma in (
        ("மரத்தினுடைய", "மரம்"),
        ("பழத்தினுடைய", "பழம்"),
        ("புத்தகத்தினுடைய", "புத்தகம்"),
        ("உலகத்தினுடைய", "உலகம்"),
    ):
        record = tokenizer.tokenize(surface)[0]
        assert record.fallback is None
        assert record.best_analysis is not None
        assert record.best_analysis.lemma == lemma
        assert "<CASE_GEN>" in record.tokens
