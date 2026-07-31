import gzip

import pytest

from tamil_morph_tokenizer import TamilWordLists


PRIVATE_WORDLISTS_AVAILABLE = TamilWordLists().lemma_dictionary_path.exists()
requires_private_wordlists = pytest.mark.skipif(
    not PRIVATE_WORDLISTS_AVAILABLE,
    reason="private lexical audit lists are intentionally absent from public releases",
)


@requires_private_wordlists
def test_dictionary_binary_search_finds_rebuilt_forms():
    wordlists = TamilWordLists()
    assert wordlists.contains_dictionary_word("மரங்களிலிருந்து")
    assert wordlists.contains_dictionary_word("படித்தான்")
    assert not wordlists.contains_dictionary_word("not-a-tamil-word")


@requires_private_wordlists
def test_lemma_dictionary_is_root_or_headword_oriented():
    wordlists = TamilWordLists()
    assert wordlists.contains_lemma("மரம்")
    assert wordlists.contains_lemma("படி")
    assert wordlists.contains_lemma("என")
    assert wordlists.contains_lemma("ஊராட்சி")
    assert not wordlists.contains_lemma("மரங்களிலிருந்து")
    assert not wordlists.contains_lemma("படித்தான்")
    assert not wordlists.contains_lemma("எனக்")
    assert not wordlists.contains_lemma("ஊராட்சித்")


@requires_private_wordlists
def test_full_surface_dictionary_excludes_sandhi_linker_surfaces():
    wordlists = TamilWordLists()
    assert wordlists.contains_dictionary_word("என")
    assert wordlists.contains_dictionary_word("ஊராட்சி")
    assert wordlists.contains_dictionary_word("ஊராட்சிக்கு")
    assert not wordlists.contains_dictionary_word("எனக்")
    assert not wordlists.contains_dictionary_word("எனச்")
    assert not wordlists.contains_dictionary_word("எனத்")
    assert not wordlists.contains_dictionary_word("ஊராட்சித்")
    assert not wordlists.contains_dictionary_word("ஊராட்சிக்குச்")


@requires_private_wordlists
def test_wordlist_source_membership_reports_sources():
    wordlists = TamilWordLists()
    sources = wordlists.source_membership("படித்தான்")
    assert "dictionary" in sources
    assert "lemma_dictionary" not in sources

    lemma_sources = wordlists.source_membership("படி")
    assert "dictionary" in lemma_sources
    assert "lemma_dictionary" in lemma_sources


def test_compressed_wordlists_are_loaded_transparently(tmp_path):
    with gzip.open(tmp_path / "tamil_dictionary.txt.gz", "wt", encoding="utf-8") as target:
        target.write("அகம்\nமரம்\n")
    with gzip.open(tmp_path / "fst_generated_forms.txt.gz", "wt", encoding="utf-8") as target:
        target.write("மரங்கள்\n")

    wordlists = TamilWordLists(wordlist_dir=tmp_path)

    assert wordlists.dictionary_path.name == "tamil_dictionary.txt.gz"
    assert wordlists.fst_generated_forms_path.name == "fst_generated_forms.txt.gz"
    assert wordlists.contains_dictionary_word("மரம்")
    assert "மரங்கள்" in wordlists.fst_generated_forms
