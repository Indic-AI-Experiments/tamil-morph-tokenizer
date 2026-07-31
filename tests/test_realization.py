import shutil

import pytest

from tamil_morph_tokenizer.analysis import parse_analysis
from tamil_morph_tokenizer.generation import FlookupGenerator
from tamil_morph_tokenizer.realization import RealizationSelector


pytestmark = pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")


def test_inverse_generator_uses_analysis_model_and_returns_all_surfaces():
    analysis = parse_analysis("மரம்+noun+pl+acc", model="noun.fst")

    assert FlookupGenerator().generate(analysis) == ("மரங்களினை", "மரங்களை")


def test_default_inverse_surface_needs_no_realization_token():
    analysis = parse_analysis("மரம்+noun+pl+acc", model="noun.fst")
    decision = RealizationSelector().select("மரங்களினை", analysis)

    assert decision.strategy == "default"
    assert decision.tokens == ()
    assert decision.selected_surface == "மரங்களினை"


def test_nondefault_inverse_surface_gets_bounded_realization_token():
    analysis = parse_analysis("மரம்+noun+pl+acc", model="noun.fst")
    decision = RealizationSelector().select("மரங்களை", analysis)

    assert decision.strategy == "variant"
    assert decision.tokens == ("<REALIZATION_1>",)
    assert decision.selected_surface == "மரங்களை"


@pytest.mark.parametrize(
    ("surface", "raw", "model"),
    [
        ("படித்தேன்", "படி+verb+fin+sim+strong+past=த்+1sg=ஏன்", "verb-c11.fst"),
        (
            "பயன்படுத்தினேன்",
            "பயன்படுத்து+verb+fin+sim+strong+past=இன்+1sg=ஏன்",
            "verb-c-rest.fst",
        ),
    ],
)
def test_exact_past_allomorphs_need_no_realization_token(surface, raw, model):
    analysis = parse_analysis(raw, model=model)
    decision = RealizationSelector().select(surface, analysis)

    assert decision.strategy == "unique"
    assert decision.tokens == ()
    assert decision.selected_surface == surface


def test_surface_outside_inverse_language_uses_byte_fallback():
    analysis = parse_analysis("மரம்+noun+pl+acc", model="noun.fst")
    decision = RealizationSelector().select("மரம்கள்", analysis)

    assert decision.strategy == "byte_fallback"
    assert not decision.exact
    assert decision.selected_surface is None
