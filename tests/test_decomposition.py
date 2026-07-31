import shutil

import pytest

from tamil_morph_tokenizer.decomposition import ProductiveCompoundLexicon
from tamil_morph_tokenizer.tokenizer import TamilMorphTokenizer


def test_reviewed_productive_compound_map_has_expected_size_and_examples():
    lexicon = ProductiveCompoundLexicon()

    assert len(lexicon) == 78_538
    assert lexicon.semantic_tokens("படித்துக்கொடு") == (
        "படி",
        "<LINK_VPART>",
        "கொடு",
    )
    assert lexicon.semantic_tokens("படிக்கப்படமுடி") == (
        "படி",
        "<VOICE_PASSIVE>",
        "<LINK_INFINITIVE>",
        "முடி",
    )
    assert lexicon.semantic_tokens("உரஞ்செய்") == (
        "உரம்",
        "<COMPOUND_LIGHT_VERB>",
        "செய்",
    )
    assert lexicon.semantic_tokens("கேட்டுப்போ") == (
        "கேள்",
        "<LINK_VPART>",
        "போ",
    )
    assert lexicon.semantic_tokens("வரப்போ") == (
        "வா",
        "<LINK_INFINITIVE>",
        "போ",
    )
    assert lexicon.semantic_tokens("நின்றுபோ") == (
        "நில்",
        "<LINK_VPART>",
        "போ",
    )


def test_source_attested_and_unresolved_compounds_remain_atomic():
    lexicon = ProductiveCompoundLexicon()

    assert lexicon.semantic_tokens("செயல்படு") == ("செயல்படு",)
    assert lexicon.semantic_tokens("தொலை") == ("தொலை",)
    assert lexicon.semantic_tokens("கோவை") == ("கோவை",)


def test_atomic_passive_stem_is_not_a_redundant_decomposition_entry():
    lexicon = ProductiveCompoundLexicon()

    assert lexicon.get("படிக்கப்படு") is None


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_auxiliary_verbal_nouns_preserve_links_and_action_nominal_semantics():
    tokenizer = TamilMorphTokenizer(mode="best")

    assert tokenizer.tokenize("போட்டியிடுவது")[0].tokens == (
        "போட்டு", "<LINK_VPART>", "இடு", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"
    )
    assert tokenizer.tokenize("ஒதுக்கிவிடுவது")[0].tokens == (
        "ஒதுக்கு", "<LINK_VPART>", "விடு", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>"
    )
    assert tokenizer.tokenize("செய்யப்படுவதும்")[0].tokens == (
        "செய்", "<VOICE_PASSIVE>", "<POS_VERBAL_NOUN>", "<ACTION_NOMINAL>",
        "<CLITIC_ADD>",
    )


def test_every_typed_decomposition_has_a_bounded_reverse_variant():
    lexicon = ProductiveCompoundLexicon()

    for lemma, decomposition in lexicon.entries().items():
        candidates = lexicon.compound_lemmas(decomposition.semantic_tokens)
        assert lemma in candidates
        assert len(candidates) <= 3
