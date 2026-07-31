from .analysis import MorphAnalysis, ParsedFlookupLine, parse_flookup_line, choose_best_analysis
from .tokenizer import TamilMorphTokenizer, TokenizedWord, is_tamil_word
from .wordlists import TamilWordLists
from .codec import ReversibleEncoding, ReversibleSpan, StructuredReversibleCodec
from .decomposition import CompoundDecomposition, CompoundLink, ProductiveCompoundLexicon
from .generation import FlookupGenerator
from .realization import RealizationDecision, RealizationSelector
from .signature import TagSignatureCodebook
from .vocabulary import FixedVocabulary
from .entity import (
    EntityAlias,
    EntityAnalyzer,
    EntityEntry,
    EntityGazetteer,
    EntitySpanMatch,
    ExactEntityAnalyzer,
    default_entity_analyzer,
    inflect_entity_form,
)

__all__ = [
    "MorphAnalysis",
    "ParsedFlookupLine",
    "parse_flookup_line",
    "choose_best_analysis",
    "TamilMorphTokenizer",
    "TokenizedWord",
    "is_tamil_word",
    "TamilWordLists",
    "FlookupGenerator",
    "RealizationDecision",
    "RealizationSelector",
    "TagSignatureCodebook",
    "ReversibleEncoding",
    "ReversibleSpan",
    "StructuredReversibleCodec",
    "CompoundDecomposition",
    "CompoundLink",
    "ProductiveCompoundLexicon",
    "FixedVocabulary",
    "EntityEntry",
    "EntityAlias",
    "EntityGazetteer",
    "EntityAnalyzer",
    "EntitySpanMatch",
    "ExactEntityAnalyzer",
    "default_entity_analyzer",
    "inflect_entity_form",
]
