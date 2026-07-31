from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

TAG_TOKEN_MAP = {
    "noun": "<POS_NOUN>",
    "compoundmodifier": "<COMPOUND_MODIFIER>",
    "verb": "<POS_VERB>",
    "adj": "<POS_ADJ>",
    "adv": "<POS_ADV>",
    "adverb": "<POS_ADV>",
    "part": "<POS_PART>",
    "particle": "<POS_PART>",
    "pp-particle": "<POSTPOSITION>",
    "pron": "<POS_PRONOUN>",
    "pronoun": "<POS_PRONOUN>",
    "quant": "<POS_QUANTIFIER>",
    "all": "<QUANT_ALL>",
    "human": "<SEM_HUMAN>",
    "poss": "<PRON_POSSESSIVE>",
    "det": "<DETERMINER>",
    "degree": "<DEGREE>",
    "comparative": "<COMPARATIVE>",
    "same": "<DEICTIC_SAME>",
    "distrib": "<DISTRIBUTIVE>",
    "dem": "<DEICTIC>",
    "demonstrative": "<DEICTIC>",
    "demonstrativeProx": "<DEICTIC_PROX>",
    "demonstrativeDist": "<DEICTIC_DIST>",
    "demonstrativeMed": "<DEICTIC_MED>",
    "prox": "<DEICTIC_PROX>",
    "dist": "<DEICTIC_DIST>",
    "med": "<DEICTIC_MED>",
    "inter": "<DEICTIC_INTERROGATIVE>",
    "time": "<DEICTIC_TIME>",
    "type": "<DEICTIC_TYPE>",
    "situation": "<DEICTIC_SITUATION>",
    "comp": "<COMPLEMENTIZER>",
    "cop": "<COPULA>",
    "copula": "<COPULA>",
    "entity_person": "<ENTITY_PERSON>",
    "entity_country": "<ENTITY_COUNTRY>",
    "entity_city": "<ENTITY_CITY>",
    "entity_region": "<ENTITY_REGION>",
    "entity_place": "<ENTITY_PLACE>",
    "entity_org": "<ENTITY_ORG>",
    "entity_brand": "<ENTITY_BRAND>",
    "entity_work": "<ENTITY_WORK>",
    "entity_other": "<ENTITY_OTHER>",
    "conjuction": "<MORPH_CONJUNCTION>",
    "conjunction": "<MORPH_CONJUNCTION>",
    "abbrev": "<ABBREVIATION>",
    "letter": "<LETTER_NAME>",
    "unit": "<MEASUREMENT_UNIT>",
    "intj": "<POS_INTERJECTION>",
    "presentative": "<PRESENTATIVE>",
    "report": "<EVIDENTIAL_REPORTATIVE>",
    "compound_light_verb": "<COMPOUND_LIGHT_VERB>",
    "become": "<COP_BECOME>",
    "modal": "<MODAL>",
    "mood": "<MOOD>",
    "attitude": "<AUX_ATTITUDINAL>",
    "nonattitude": "<AUX_NONATTITUDINAL>",
    "exist": "<EXISTENTIAL>",
    "ques": "<MOOD_QUESTION>",
    "prohib": "<MOOD_PROHIBITIVE>",
    "sandhik": "<SANDHI_K>",
    "sandhic": "<SANDHI_C>",
    "sandhip": "<SANDHI_P>",
    "sandhit": "<SANDHI_T>",
    "sg": "<NUM_SG>",
    "pl": "<NUM_PL>",
    "nom": "<CASE_NOM>",
    "acc": "<CASE_ACC>",
    "dat": "<CASE_DAT>",
    "gen": "<CASE_GEN>",
    "inst": "<CASE_INST>",
    "trans": "<CASE_TRANS>",
    "casemarker": "<CASE_MARKER>",
    "loc": "<CASE_LOC>",
    "abl": "<CASE_ABL>",
    "soc": "<CASE_SOC>",
    "voc": "<CASE_VOC>",
    "add": "<CLITIC_ADD>",
    "foc": "<CLITIC_FOCUS>",
    "indef": "<INDEFINITE>",
    "fin": "<VERB_FINITE>",
    "nonfin": "<VERB_NONFINITE>",
    "sim": "<VERB_SIMPLE>",
    "strong": "<VERB_STRONG>",
    "weak": "<VERB_WEAK>",
    "middle": "<VERB_MIDDLE>",
    "complex": "<VERB_COMPLEX>",
    "caus": "<VOICE_CAUSATIVE>",
    "aspect": "<ASPECT>",
    "perfect": "<ASPECT_PERFECT>",
    "prospective": "<ASPECT_PROSPECTIVE>",
    "passive": "<VOICE_PASSIVE>",
    "past": "<TENSE_PAST>",
    "pres": "<TENSE_PRESENT>",
    "fut": "<TENSE_FUTURE>",
    "inf": "<VERB_INFINITIVE>",
    "infInc": "<STEM_OBLIQUE>",
    "imp": "<VERB_IMPERATIVE>",
    "opt": "<MOOD_OPTATIVE>",
    "con": "<MOOD_CONDITIONAL>",
    "cond": "<MOOD_CONDITIONAL>",
    "euph": "<EUPHONIC_AUGMENT>",
    "verbalnoun": "<POS_VERBAL_NOUN>",
    "actionnominal": "<ACTION_NOMINAL>",
    "pos": "<POLARITY_POS>",
    "neg": "<POLARITY_NEG>",
    "1sg": "<PERSON_1SG>",
    "2sg": "<PERSON_2SG>",
    "2sgm": "<PERSON_2SG_MASC>",
    "2sgf": "<PERSON_2SG_FEM>",
    "2sgn": "<PERSON_2SG_NEUT>",
    "2sgh": "<PERSON_2SG_HON>",
    "2plh": "<PERSON_2PL_HON>",
    "3sg": "<PERSON_3SG>",
    "3sgh": "<PERSON_3SG_HON>",
    "3sgm": "<PERSON_3SG_MASC>",
    "3sgf": "<PERSON_3SG_FEM>",
    "3sge": "<PERSON_3SG_EPICENE>",
    "3sghe": "<PERSON_3SG_HON>",
    "3sgn": "<PERSON_3SG_NEUT>",
    "1pl": "<PERSON_1PL>",
    "2pl": "<PERSON_2PL>",
    "3pl": "<PERSON_3PL>",
    "3plh": "<PERSON_3PL_HON>",
    "3ple": "<PERSON_3PL_EPICENE>",
    "3pln": "<PERSON_3PL_NEUT>",
    "adjpart": "<ADJECTIVAL_PARTICIPLE>",
    "PartNoun": "<POS_PARTICIPIAL_NOUN>",
    "vpart": "<VERBAL_PARTICIPLE>",
    "futANDadjpart": "<FUTURE_ADJECTIVAL_PARTICIPLE>",
    "negpart": "<NEGATIVE_PARTICIPLE>",
    "moodpart": "<MOOD_PARTICLE>",
    "worthy": "<MODAL_WORTHY>",
    "link_vpart": "<LINK_VPART>",
    "link_inf": "<LINK_INFINITIVE>",
    "cardinal": "<NUM_CARDINAL>",
    "ordinal": "<NUM_ORDINAL>",
    "fraction": "<NUM_FRACTION>",
    "intensifier": "<INTENSIFIER>",
    "privative": "<PRIVATIVE_WITHOUT>",
    "honorific_title": "<TITLE_HONORIFIC>",
    "colloq": "<REGISTER_COLLOQUIAL>",
    "incl": "<PRON_INCLUSIVE>",
    "excl": "<PRON_EXCLUSIVE>",
    "pssd": "<PRON_POSSESSIVE>",
    "refl": "<PRON_REFLEXIVE>",
    "psp_aattam": "<DERIV_AATTAM>",
    "psp_mathiri": "<POST_LIKE_AS>",
    "psp_padi": "<POST_ACCORDING_TO>",
    "psp_idaiye": "<POST_AMONG>",
    "psp_ul": "<POST_WITHIN_BY>",
    "recip": "<RECIPROCAL>",
    "redup": "<REDUPLICATION>",
    "purpose": "<SEM_PURPOSE>",
    "vpart_nookki": "<POST_TOWARD>",
    "vpart_parttu": "<REL_ATTACH>",
    "vpart_patti": "<POST_ABOUT>",
    "vpart_pin": "<POST_AFTER>",
    "vpart_potu": "<TEMPORAL_WHEN>",
    "vpart_maaru": "<MANNER_PURPOSE>",
    "vpart_tum": "<TEMPORAL_IMMEDIATE>",
}

POS_RANK = {
    "quant": 0,
    "pron": 0,
    "pronoun": 0,
    "dem": 0,
    "modal": 0,
    "exist": 0,
    "pp-particle": 0,
    "comp": 0,
    "cop": 0,
    "entity_person": 3,
    "entity_country": 0,
    "entity_city": 3,
    "entity_region": 0,
    "entity_place": 3,
    "entity_org": 0,
    "entity_brand": 3,
    "entity_work": 3,
    "entity_other": 3,
    "verb": 1,
    "noun": 2,
    "adj": 3,
    "adv": 4,
    "part": 5,
    "intj": 5,
}

NOUN_CASE_RANK = {
    "loc": 0,
    "abl": 1,
    "soc": 1,
}

DERIVABLE_VERB_TAGS = {
    "verb",
    "fin",
    "nonfin",
    "sim",
    "complex",
    "strong",
    "weak",
    "middle",
    "attitude",
    "nonattitude",
    "aspect",
    "mood",
}

@dataclass(frozen=True)
class MorphAnalysis:
    raw: str
    lemma: str
    tags: tuple[str, ...]
    morph_tokens: tuple[str, ...]
    model: str | None = None

    @property
    def is_recognized(self) -> bool:
        return self.raw != "+?" and bool(self.lemma)

@dataclass(frozen=True)
class ParsedFlookupLine:
    surface: str
    analysis: MorphAnalysis


def normalize_tag(tag: str) -> str:
    """Drop FST realization material such as past=த் or 1sg=ஏன்."""
    return tag.split("=", 1)[0]


def tag_to_token(tag: str) -> str:
    if tag.startswith(("auxlemma:", "lexlemma:")):
        return tag.split(":", 1)[1]
    normalized = normalize_tag(tag)
    mapped = TAG_TOKEN_MAP.get(normalized)
    if mapped:
        return mapped
    safe = normalized.upper().replace("-", "_")
    return f"<MORPH_{safe}>"


def semantic_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
    normalized_items: list[str] = []
    for tag in tags:
        normalized = normalize_tag(tag)
        if normalized in {"aux", "auxinf"} and "=" in tag:
            auxiliary_lemma = tag.split("=", 1)[1]
            link = "link_inf" if normalized == "auxinf" else "link_vpart"
            normalized_items.extend((link, f"auxlemma:{auxiliary_lemma}"))
        elif normalized == "lightaux" and "=" in tag:
            auxiliary_lemma = tag.split("=", 1)[1]
            normalized_items.extend(("compound_light_verb", f"auxlemma:{auxiliary_lemma}"))
        elif normalized == "lexlemma" and "=" in tag:
            normalized_items.append(f"lexlemma:{tag.split('=', 1)[1]}")
        else:
            normalized_items.append(normalized)
    normalized = tuple(normalized_items)
    # The upstream prebuilt pronoun FST labels proximal third-person
    # demonstratives with second-person tags. Correct only that context.
    if "pron" in normalized and "dem" in normalized:
        demonstrative_person = {
            "2sgm": "3sgm",
            "2sgf": "3sgf",
            "2sgn": "3sgn",
            "2sgh": "3sgh",
            "2pl": "3pl",
        }
        normalized = tuple(demonstrative_person.get(tag, tag) for tag in normalized)
        # The upstream pronoun relation contains both duplicated `dem` tags
        # and equivalent feature bundles emitted in construction-dependent
        # orders. Preserve the raw analysis in MorphAnalysis.tags, but expose
        # one canonical semantic reading to models.
        pronoun_priority = {
            "pron": 0,
            "dem": 10,
            "prox": 20,
            "med": 20,
            "dist": 20,
            "inter": 20,
            "1sg": 30,
            "2sg": 30,
            "3sg": 30,
            "1pl": 30,
            "2pl": 30,
            "3pl": 30,
            "3sgm": 30,
            "3sgf": 30,
            "3sgn": 30,
            "3sgh": 30,
            "3pln": 30,
            "nom": 90,
            "acc": 90,
            "dat": 90,
            "gen": 90,
            "inst": 90,
            "soc": 90,
            "loc": 90,
            "abl": 90,
        }
        deduplicated = tuple(dict.fromkeys(normalized))
        normalized = tuple(
            tag
            for _, tag in sorted(
                enumerate(deduplicated),
                key=lambda item: (
                    pronoun_priority.get(item[1], 50),
                    item[0],
                ),
            )
        )
    if "verb" in normalized:
        normalized = tuple(tag for tag in normalized if tag not in DERIVABLE_VERB_TAGS)
    if "verbalnoun" not in normalized:
        return normalized
    result: list[str] = []
    for tag in normalized:
        result.append(tag)
        if tag == "verbalnoun":
            result.append("actionnominal")
    return tuple(result)


def parse_analysis(raw_analysis: str, model: str | None = None) -> MorphAnalysis:
    raw_analysis = raw_analysis.strip()
    if raw_analysis == "+?" or not raw_analysis:
        return MorphAnalysis(raw=raw_analysis or "+?", lemma="", tags=(), morph_tokens=(), model=model)

    parts = raw_analysis.split("+")
    lemma = parts[0]
    tags = tuple(part for part in parts[1:] if part)
    morph_tokens = tuple(tag_to_token(tag) for tag in semantic_tags(tags))
    return MorphAnalysis(raw=raw_analysis, lemma=lemma, tags=tags, morph_tokens=morph_tokens, model=model)


def parse_flookup_line(line: str, model: str | None = None) -> ParsedFlookupLine | None:
    line = line.rstrip("\n")
    if not line:
        return None
    if "\t" not in line:
        return None
    surface, raw_analysis = line.split("\t", 1)
    return ParsedFlookupLine(surface=surface, analysis=parse_analysis(raw_analysis, model=model))


def noun_case_rank(normalized_tags: list[str]) -> int:
    if not ({"noun", "pron", "pronoun"} & set(normalized_tags)):
        return 0
    return min((NOUN_CASE_RANK[tag] for tag in normalized_tags if tag in NOUN_CASE_RANK), default=0)


def analysis_score(analysis: MorphAnalysis) -> tuple[int, int, int, int, int, str]:
    if not analysis.is_recognized:
        return (999, 999, 999, 999, 999, analysis.raw)
    normalized_tags = [normalize_tag(tag) for tag in analysis.tags]
    pos_rank = min((POS_RANK[tag] for tag in normalized_tags if tag in POS_RANK), default=50)
    if "verb" in normalized_tags and "verbalnoun" in normalized_tags:
        # Productive negative action nominals are more informative than a
        # generic noun homograph. Positive lexicalized nominals still prefer
        # their standalone noun reading (for example, தேர்தல்).
        pos_rank = POS_RANK["verb"] if "neg" in normalized_tags else POS_RANK["noun"] + 1
    if "verb" in normalized_tags and "imp" in normalized_tags:
        # A bare imperative depends on discourse context. When the same surface
        # has an independently attested nominative noun reading, prefer the
        # lexical noun for isolated-token ranking and preserve the imperative
        # as an alternate analysis.
        pos_rank = POS_RANK["noun"] + 1
    finite_bonus = 0 if "fin" in normalized_tags else 1
    specificity = -len(normalized_tags)
    lemma_length = len(analysis.lemma)
    return (pos_rank, finite_bonus, specificity, lemma_length, noun_case_rank(normalized_tags), analysis.raw)


def choose_best_analysis(analyses: Iterable[MorphAnalysis]) -> MorphAnalysis | None:
    recognized = [analysis for analysis in analyses if analysis.is_recognized]
    if not recognized:
        return None
    has_nominative_noun = any(
        {normalize_tag(tag) for tag in analysis.tags} >= {"noun", "nom"}
        for analysis in recognized
    )
    has_genitive_additive_noun = any(
        {normalize_tag(tag) for tag in analysis.tags} >= {"noun", "gen", "add"}
        for analysis in recognized
    )
    has_translative_noun = any(
        {normalize_tag(tag) for tag in analysis.tags} >= {"noun", "trans"}
        and "verb" not in {normalize_tag(tag) for tag in analysis.tags}
        for analysis in recognized
    )
    has_instrumental_noun = any(
        {normalize_tag(tag) for tag in analysis.tags} >= {"noun", "inst"}
        for analysis in recognized
    )
    unmarked_verbal_noun_lemmas = {
        analysis.lemma
        for analysis in recognized
        if {normalize_tag(tag) for tag in analysis.tags} >= {"verb", "verbalnoun"}
        and "fut" not in {normalize_tag(tag) for tag in analysis.tags}
    }

    def contextual_score(analysis: MorphAnalysis) -> tuple[int, int, int, int, int, str]:
        score = analysis_score(analysis)
        normalized_tags = {normalize_tag(tag) for tag in analysis.tags}
        if "intensifier" in normalized_tags:
            return (-1, *score[1:])
        if {"intj", "voc"} <= normalized_tags:
            return (-1, *score[1:])
        if (
            has_nominative_noun
            and {"noun", "trans", "colloq"} <= normalized_tags
        ):
            # A lexical nominative such as அக்கா outranks a coincidentally
            # identical spoken translative (அக்கு + -ஆ) in isolation.
            return (POS_RANK["noun"] + 1, *score[1:])
        if has_nominative_noun and {"noun", "voc"} <= normalized_tags:
            # In isolation, an attested citation-form noun is a safer default
            # than a homographic vocative derived from another lemma. Both
            # readings remain available in compact-ambiguity mode.
            return (POS_RANK["noun"] + 1, *score[1:])
        if (
            has_translative_noun
            and {"noun", "verb", "become", "inf"} <= normalized_tags
        ):
            # Bare -ஆக and its clitic/sandhi extensions are genuinely
            # ambiguous with the infinitive of ஆகு. Prefer the ordinary
            # translative/adverbial reading in isolation and retain both.
            return (POS_RANK["noun"] + 1, *score[1:])
        if (
            has_instrumental_noun
            and {"verb", "con"} <= normalized_tags
        ):
            # In isolation, an overt nominal instrumental is the conservative
            # modern-prose default for surfaces such as மரத்தால். The valid
            # verb conditional remains available as an alternate analysis.
            return (POS_RANK["noun"] + 1, *score[1:])
        if "adv" in normalized_tags and normalized_tags & {"time", "situation"}:
            # Lexicalized deictic discourse adverbs are more specific than
            # their valid compositional determiner+noun readings.
            return (-1, *score[1:])
        if (
            has_genitive_additive_noun
            and {"verb", "verbalnoun", "add"} <= normalized_tags
        ):
            return (POS_RANK["verb"], *score[1:])
        if (
            has_nominative_noun
            and "verb" in normalized_tags
            and "vpart" in normalized_tags
            and "verbalnoun" not in normalized_tags
            and "neg" not in normalized_tags
            and "colloq" not in normalized_tags
        ):
            return (POS_RANK["noun"] + 1, *score[1:])
        if (
            analysis.lemma in unmarked_verbal_noun_lemmas
            and {"verb", "verbalnoun", "fut"} <= normalized_tags
        ):
            # Forms in -வது can carry a future/nonpast participial reading as
            # well as an unmarked action-nominal reading. Preserve both, but
            # do not let the extra future tag win ranking by specificity alone.
            return (score[0], score[1], score[2] + 100, *score[3:])
        return score

    return min(recognized, key=contextual_score)
