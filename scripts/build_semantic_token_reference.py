#!/usr/bin/env python3
"""Build the public, exhaustive semantic-factor vocabulary reference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_DIR = ROOT / "tamil_morph_tokenizer/data/vocabulary"
DEFAULT_JSON = VOCABULARY_DIR / "semantic_token_reference.json"
DEFAULT_DOC = ROOT / "docs/SEMANTIC_TOKEN_VOCABULARY.md"


CATEGORY_PREFIXES = (
    ("<POS_", "part of speech"),
    ("<CASE_", "case"),
    ("<PERSON_", "person and agreement"),
    ("<TENSE_", "tense"),
    ("<ASPECT_", "aspect"),
    ("<VOICE_", "voice"),
    ("<MOOD_", "mood"),
    ("<MODAL", "modality"),
    ("<NUM_", "number and quantity"),
    ("<PRON_", "pronoun"),
    ("<DEICTIC", "deixis"),
    ("<ENTITY_", "named entity"),
    ("<POST", "postposition and relation"),
    ("<CLITIC_", "clitic"),
    ("<SANDHI_", "sandhi"),
    ("<POLARITY_", "polarity"),
    ("<VERB_", "verb form"),
    ("<VERBAL_", "verb form"),
    ("<ADJECTIVAL_", "participle"),
    ("<FUTURE_ADJECTIVAL_", "participle"),
    ("<NEGATIVE_PARTICIPLE", "participle"),
    ("<MORPH_PSP_", "legacy postposition"),
    ("<MORPH_VPART", "legacy verbal relation"),
    ("<MORPH_", "legacy FST label"),
)


EXACT_DESCRIPTIONS = {
    "<ABBREVIATION>": "Marks an abbreviation.",
    "<ACTION_NOMINAL>": "Marks a verb-derived noun that names an action or event.",
    "<ADJECTIVAL_PARTICIPLE>": "Marks a verb form used to modify a noun.",
    "<ASPECT_PERFECT>": "Marks a completed action or a resulting state.",
    "<ASPECT_PROSPECTIVE>": "Marks an action viewed as expected or about to happen.",
    "<AUX_ATTITUDINAL>": "Broad inherited FST label for an auxiliary construction that expresses the speaker's stance.",
    "<CASE_ABL>": "Ablative case: from, out of, or away from.",
    "<CASE_ACC>": "Accusative case: usually the direct object.",
    "<CASE_DAT>": "Dative case: usually to or for.",
    "<CASE_GEN>": "Genitive case: possession or an of-relation.",
    "<CASE_INST>": "Instrumental case: by, with, or using.",
    "<CASE_LOC>": "Locative case: in, at, or on.",
    "<CASE_MARKER>": "Broad inherited FST label indicating that a case marker is present.",
    "<CASE_NOM>": "Nominative or unmarked base case, often used for the subject.",
    "<CASE_SOC>": "Sociative case: with or together with.",
    "<CASE_TRANS>": "Translative or adverbial case-like form: as, becoming, or in a stated manner.",
    "<CASE_VOC>": "Vocative case used for direct address.",
    "<CLITIC_ADD>": "Additive clitic: also, too, or and.",
    "<CLITIC_FOCUS>": "Focus or emphatic clitic, often corresponding to தான்.",
    "<COMPARATIVE>": "Marks a comparison such as than, more, or less.",
    "<COMPLEMENTIZER>": "Introduces a quoted, reported, or embedded clause.",
    "<COMPOUND_MODIFIER>": "Marks a noun used attributively before another word in a compound.",
    "<COPULA>": "Marks a copular expression that links a subject with a description or identity.",
    "<COP_BECOME>": "Marks a change into a state: become.",
    "<DEGREE>": "Marks an amount or degree expression.",
    "<DEICTIC>": "General demonstrative or pointing meaning.",
    "<DEICTIC_DIST>": "Distal demonstrative: that, there, or then.",
    "<DEICTIC_INTERROGATIVE>": "Interrogative demonstrative: which, where, or when.",
    "<DEICTIC_MED>": "Medial demonstrative: an intermediate distance.",
    "<DEICTIC_PROX>": "Proximal demonstrative: this, here, or now.",
    "<DEICTIC_SAME>": "Marks identity or sameness: the same.",
    "<DEICTIC_SITUATION>": "Points to a situation or context.",
    "<DEICTIC_TIME>": "Points to a time.",
    "<DEICTIC_TYPE>": "Points to a kind or type.",
    "<DERIV_AATTAM>": "Marks the ஆட்டம்-derived manner or likeness construction.",
    "<DETERMINER>": "Marks a word that specifies or limits a noun.",
    "<DISTRIBUTIVE>": "Distributive meaning: each, respective, or one by one.",
    "<EUPHONIC_AUGMENT>": "Marks an inserted sound used to join morphemes smoothly.",
    "<EVIDENTIAL_REPORTATIVE>": "Marks information presented as reported rather than directly witnessed.",
    "<EXISTENTIAL>": "Marks existence or availability.",
    "<FUTURE_ADJECTIVAL_PARTICIPLE>": "Marks a future-oriented verb form used to modify a noun.",
    "<INDEFINITE>": "Marks an indefinite meaning such as some or any.",
    "<LETTER_NAME>": "Marks a spoken or written letter name.",
    "<MANNER_PURPOSE>": "Marks a directed manner or intended outcome, often in -உமாறு.",
    "<MEASUREMENT_UNIT>": "Marks a unit of measurement.",
    "<MODAL>": "Broad modal meaning such as ability, necessity, or possibility.",
    "<MODAL_MUST>": "Necessity or obligation: must, should, or need to.",
    "<MODAL_WORTHY>": "Marks suitability or worthiness.",
    "<MOOD_CONDITIONAL>": "Conditional mood: if or under a condition.",
    "<MOOD_OPTATIVE>": "Optative mood: a wish, hope, or blessing.",
    "<MOOD_PARTICLE>": "Marks a particle that contributes mood.",
    "<MOOD_PROHIBITIVE>": "Negative command: do not.",
    "<MOOD_QUESTION>": "Marks a question.",
    "<NEGATIVE_PARTICIPLE>": "Marks a negative non-finite or modifying verb form.",
    "<NUM_CARDINAL>": "Cardinal number: one, two, three, and so on.",
    "<NUM_FRACTION>": "Fractional number.",
    "<NUM_ORDINAL>": "Ordinal number: first, second, and so on.",
    "<NUM_PL>": "Plural number.",
    "<NUM_SG>": "Singular number.",
    "<PART_ONLY>": "Restrictive particle: only or just.",
    "<POLARITY_NEG>": "Negative polarity.",
    "<POLARITY_POS>": "Positive polarity.",
    "<POSTPOSITION>": "General postposition or relational function word.",
    "<POST_ABOUT>": "Relation meaning about or concerning.",
    "<POST_ACCORDING_TO>": "Relation meaning according to or in the manner stated.",
    "<POST_AFTER>": "Temporal or spatial relation meaning after or behind.",
    "<POST_AMONG>": "Relation meaning among or between.",
    "<POST_BEFORE>": "Temporal or spatial relation meaning before or in front of.",
    "<POST_LIKE_AS>": "Similarity relation: like or as.",
    "<POST_TOWARD>": "Direction relation: toward.",
    "<POST_UNTIL>": "Boundary relation: until or up to.",
    "<POST_WITHIN_BY>": "Interior or deadline relation: within, inside, or by.",
    "<PRESENTATIVE>": "Presentative expression used to point out or introduce something.",
    "<PRIVATIVE_WITHOUT>": "Privative meaning: without or lacking.",
    "<QUANT_ALL>": "Universal quantity: all or every.",
    "<RECIPROCAL>": "Reciprocal relation: each other.",
    "<REDUPLICATION>": "Marks a repeated form used for distribution, emphasis, or iteration.",
    "<REGISTER_COLLOQUIAL>": "Marks a colloquial form.",
    "<REL_ATTACH>": "Marks an attaching or related-to construction.",
    "<SEM_HUMAN>": "Marks reference to a human being or group.",
    "<SEM_PURPOSE>": "Marks purpose or intended use.",
    "<STEM_OBLIQUE>": "Marks a changed noun stem used before a case ending.",
    "<TEMPORAL_IMMEDIATE>": "Marks immediate succession: as soon as.",
    "<TEMPORAL_WHEN>": "Marks a time relation: when or while.",
    "<TITLE_HONORIFIC>": "Marks an honorific title.",
    "<VERBAL_PARTICIPLE>": "Marks a non-finite verb that links to a following action.",
    "<VERB_COMPLEX>": "Broad inherited FST label for a complex verb construction.",
    "<VERB_FINITE>": "Broad inherited FST label for a finite verb.",
    "<VERB_IMPERATIVE>": "Imperative verb form: a command or request.",
    "<VERB_INFINITIVE>": "Infinitive verb form.",
    "<VERB_NONFINITE>": "Broad inherited FST label for a non-finite verb.",
    "<VOICE_CAUSATIVE>": "Causative voice: causes someone or something to act.",
    "<VOICE_PASSIVE>": "Passive voice: presents the affected participant rather than the actor.",
}


PERSON_DESCRIPTIONS = {
    "1SG": "First person singular: I.",
    "1PL": "First person plural: we.",
    "2SG": "Second person singular: you.",
    "2SG_HON": "Second person singular honorific: respectful you.",
    "2PL": "Second person plural: you (plural).",
    "2PL_HON": "Second person plural honorific: respectful you.",
    "3SG": "Third person singular.",
    "3SG_MASC": "Third person singular masculine: he.",
    "3SG_FEM": "Third person singular feminine: she.",
    "3SG_NEUT": "Third person singular neuter: it.",
    "3SG_EPICENE": "Third person singular without a masculine/feminine distinction.",
    "3SG_HON": "Third person singular honorific.",
    "3PL": "Third person plural: they.",
    "3PL_NEUT": "Third person plural neuter or non-human.",
    "3PL_EPICENE": "Third person plural without a masculine/feminine distinction.",
}


ENTITY_DESCRIPTIONS = {
    "BRAND": "Named entity: brand.",
    "CITY": "Named entity: city.",
    "COUNTRY": "Named entity: country.",
    "ORG": "Named entity: organization.",
    "OTHER": "Named entity: other reviewed entity type.",
    "PERSON": "Named entity: person.",
    "PLACE": "Named entity: place.",
    "REGION": "Named entity: region.",
    "WORK": "Named entity: named creative work.",
}


POS_DESCRIPTIONS = {
    "ADJ": "Part of speech: adjective.",
    "ADV": "Part of speech: adverb.",
    "INTERJECTION": "Part of speech: interjection.",
    "NOUN": "Part of speech: noun.",
    "PART": "Part of speech: particle.",
    "PARTICIPIAL_NOUN": "Part of speech: noun formed from a participle.",
    "PRONOUN": "Part of speech: pronoun.",
    "QUANTIFIER": "Part of speech: quantifier.",
    "VERBAL_NOUN": "Part of speech: verb-derived action or event noun.",
}


PRONOUN_DESCRIPTIONS = {
    "EXCLUSIVE": "Exclusive first-person plural: we, excluding the addressee.",
    "INCLUSIVE": "Inclusive first-person plural: we, including the addressee.",
    "POSSESSIVE": "Possessive pronoun function.",
    "REFLEXIVE": "Reflexive pronoun function: self.",
}


TAMIL_GLOSSES = {
    "ஃபாசிசம்": "fascism",
    "அஃகடி": "difficulty, trouble, or peril",
    "அஃகம்": "grain or spring water, depending on the lexical reading",
    "அஃகரம்": "the white madar shrub",
    "அடிப்படை": "basis or foundation",
    "அடுத்து": "next or following",
    "அடை": "reach or attain",
    "அன்று": "that day; not",
    "அல்லு": "be not",
    "அழுத்தம்": "pressure",
    "ஆண்டு": "year; rule",
    "இடம்": "place",
    "இரண்டு": "two",
    "இரவு": "night",
    "இரு": "be, remain, or continue",
    "இறங்கு": "descend",
    "இல்லை": "not exist; no",
    "உட்படு": "be included or subjected",
    "உரிய": "appropriate or belonging to",
    "உலகம்": "world",
    "உள்": "inside; exist",
    "ஏற்ப": "according to; accept",
    "ஒட்டி": "adjoining or in connection with",
    "ஒன்று": "one",
    "ஒரு": "one or a",
    "ஒருவர்": "one person",
    "கட்டம்": "stage or block",
    "குறித்த": "about or concerning",
    "கூடு": "be possible; join",
    "கூறு": "say; component",
    "கொள்": "take; reflexive or completive light verb",
    "சில": "some",
    "தவிர": "except",
    "தொடர்": "continue or follow",
    "தொடர்பு": "connection",
    "நபர்": "person",
    "நிலை": "state or condition",
    "நேரம்": "time",
    "பற்றி": "about or concerning",
    "பின்னர்": "afterwards",
    "புறம்": "side or outside",
    "பேர்": "person or name",
    "போது": "when or time",
    "போன்ற": "like or similar to",
    "போன்று": "like or in the manner of",
    "போல்": "like or as",
    "மக்கள்": "people",
    "மட்டும்": "only; up to",
    "மாட்டு": "will not; be unable",
    "முடி": "finish; be able",
    "மூலம்": "through or by means of",
    "வகை": "kind or type",
    "வரை": "until or up to",
    "வரையில்": "until or within the stated limit",
    "வா": "come",
    "வாய்": "mouth; by way of",
    "வாறு": "manner or way",
    "விட": "than; leave",
    "விடு": "leave, release, or completive light verb",
    "விதம்": "kind or manner",
    "வேண்டு": "need or want",
    "வேளை": "time or occasion",
}


LEGACY_GLOSSES = {
    "AFFIRM": "affirmative meaning",
    "ALT": "alternative form or reading",
    "BEN": "benefactive meaning",
    "CMPR": "comparative meaning",
    "CONJUNCTION": "conjunction",
    "DEICTIC": "deictic or demonstrative meaning",
    "EXCLAM": "exclamation",
    "INT": "intensifying or interrogative legacy label",
    "INTERJECTION": "interjection",
    "INTERROGATIVE": "interrogative meaning",
    "LIMIT": "limit or restriction",
    "LOAN": "loanword",
    "NEUT": "neuter agreement or class",
    "N_PATHIL": "noun-based பதில் relational construction",
    "OTHER": "other inherited FST category",
    "PRIV": "privative meaning",
    "REGISTER": "register label",
    "SANDHI_C": "legacy c-type sandhi",
    "SANDHI_K": "legacy k-type sandhi",
    "SANDHI_P": "legacy p-type sandhi",
    "SANDHI_T": "legacy t-type sandhi",
    "UNTIL": "until or boundary meaning",
}


PSP_GLOSSES = {
    "ALLAAMAL": "without",
    "APPAAL": "beyond or on the other side",
    "APPURAM": "after",
    "ARUKIL": "near",
    "ATIYIL": "under or at the foot of",
    "ETHIR": "opposite or against",
    "ETHIRE": "opposite or facing",
    "IDAIYIL": "between or among",
    "IDAIYL": "between or among",
    "IDAYIL": "between or among",
    "ILLAAMAL": "without",
    "KEEL": "below",
    "KEELE": "below",
    "KURUKKE": "across",
    "MEEL": "above or on",
    "MEELE": "above or on",
    "MUN": "before or in front of",
    "MUNNAAL": "before",
    "MUNNE": "before or in front",
    "NADUVIL": "in the middle of",
    "PIN": "after or behind",
    "PINNAAL": "after or behind",
    "PINNE": "after or behind",
    "PIRAKU": "after",
    "POL": "like or as",
    "POLA": "like or as",
    "TAVIRA": "except",
    "UL": "inside",
    "ULE": "inside",
    "ULLE": "inside",
    "VALIYAAKA": "through or by way of",
    "VARAIKKUM": "until or up to",
    "VARAIYIL": "until or within the limit",
    "VELIYEE": "outside",
    "VELIYIL": "outside",
}


VPART_GLOSSES = {
    "CUTTI": "around or concerning",
    "KONDU": "with, by, or while doing",
    "OTTI": "adjoining or in relation to",
    "TAANDI": "beyond or crossing",
    "TAVIRTU": "excluding or avoiding",
    "VAITTU": "using, keeping, or having done",
    "VIDA": "than or leaving",
}


def semantic_tokens() -> list[str]:
    manifest = json.loads((VOCABULARY_DIR / "manifest.json").read_text())
    tokens = (VOCABULARY_DIR / "tokens.txt").read_text(encoding="utf-8").splitlines()
    semantic_count = int(manifest["counts"]["semantic_tokens"])
    lemma_count = int(manifest["counts"]["lemmas"])
    start = len(tokens) - lemma_count - semantic_count
    return tokens[start : start + semantic_count]


def category_for(token: str) -> str:
    if not token.startswith("<"):
        return "Tamil lexical factor"
    for prefix, category in CATEGORY_PREFIXES:
        if token.startswith(prefix):
            return category
    return "grammatical or semantic feature"


def description_for(token: str) -> str:
    if token in EXACT_DESCRIPTIONS:
        return EXACT_DESCRIPTIONS[token]
    if not token.startswith("<"):
        gloss = TAMIL_GLOSSES.get(token)
        if gloss:
            return f"Tamil lexical factor meaning {gloss}; retained by lemma identity inside an analysis."
        return (
            f"Tamil lexical factor `{token}` retained by lemma identity inside an "
            "analysis; it is not a generic grammar label."
        )
    inner = token[1:-1]
    if inner.startswith("PERSON_"):
        return PERSON_DESCRIPTIONS[inner.removeprefix("PERSON_")]
    if inner.startswith("ENTITY_"):
        return ENTITY_DESCRIPTIONS[inner.removeprefix("ENTITY_")]
    if inner.startswith("POS_"):
        return POS_DESCRIPTIONS[inner.removeprefix("POS_")]
    if inner.startswith("PRON_"):
        return PRONOUN_DESCRIPTIONS[inner.removeprefix("PRON_")]
    if inner.startswith("TENSE_"):
        return f"{inner.removeprefix('TENSE_').title()} tense."
    if inner.startswith("SANDHI_"):
        return f"Marks {inner.removeprefix('SANDHI_').lower()}-type linking sandhi."
    if inner.startswith("MORPH_PSP_"):
        raw = inner.removeprefix("MORPH_PSP_")
        from_relation = raw.endswith("_IRUNTU")
        base = raw.removesuffix("_IRUNTU")
        gloss = PSP_GLOSSES.get(base, base.lower().replace("_", " "))
        if from_relation:
            gloss = f"from {gloss}"
        return (
            f"Legacy FST postposition label meaning {gloss}. It remains fixed in "
            "the released vocabulary pending a narrower named mapping."
        )
    if inner.startswith("MORPH_VPARTP_"):
        raw = inner.removeprefix("MORPH_VPARTP_")
        gloss = VPART_GLOSSES.get(raw, raw.lower().replace("_", " "))
        return f"Legacy participial relation meaning {gloss}."
    if inner.startswith("MORPH_VPART_"):
        raw = inner.removeprefix("MORPH_VPART_")
        gloss = VPART_GLOSSES.get(raw, raw.lower().replace("_", " "))
        return f"Legacy verbal-participle relation meaning {gloss}."
    if inner.startswith("MORPH_"):
        raw = inner.removeprefix("MORPH_")
        gloss = LEGACY_GLOSSES.get(raw, raw.lower().replace("_", " "))
        return (
            f"Legacy FST label for {gloss}; retained as a fixed readable factor "
            "rather than created dynamically."
        )
    return f"Fixed feature for {inner.lower().replace('_', ' ')}."


def source_for(token: str) -> str:
    if not token.startswith("<"):
        return "FST-derived lexical factor"
    if token.startswith("<MORPH_"):
        return "normalized inherited FST tag"
    if token in {
        "<ACTION_NOMINAL>",
        "<COP_BECOME>",
        "<SEM_HUMAN>",
        "<SEM_PURPOSE>",
    }:
        return "project semantic mapping"
    if token in {
        "<MODAL_MUST>",
        "<PART_ONLY>",
        "<POST_BEFORE>",
        "<POST_UNTIL>",
    }:
        return "reviewed lexical special or FST mapping"
    return "mapped FST tag or reviewed semantic mapping"


def records() -> list[dict[str, object]]:
    tokens = semantic_tokens()
    first_id = len(
        (VOCABULARY_DIR / "tokens.txt").read_text(encoding="utf-8").splitlines()
    ) - len(tokens) - int(
        json.loads((VOCABULARY_DIR / "manifest.json").read_text())["counts"]["lemmas"]
    )
    return [
        {
            "id": first_id + index,
            "token": token,
            "category": category_for(token),
            "description": description_for(token),
            "source": source_for(token),
        }
        for index, token in enumerate(tokens)
    ]


def markdown_table(
    items: list[dict[str, object]],
    *,
    include_source: bool = True,
) -> str:
    lines = (
        [
            "| ID | Token | Family | Meaning | Source |",
            "| ---: | --- | --- | --- | --- |",
        ]
        if include_source
        else [
            "| ID | Token | Family | Meaning |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for item in items:
        description = str(item["description"]).replace("|", "\\|")
        source = str(item["source"]).replace("|", "\\|")
        row = (
            f"| {item['id']} | `{item['token']}` | {item['category']} | "
            f"{description}"
        )
        lines.append(f"{row} | {source} |" if include_source else f"{row} |")
    return "\n".join(lines)


def public_doc(
    label_items: list[dict[str, object]],
    lexical_items: list[dict[str, object]],
) -> str:
    counts: dict[str, int] = {}
    for item in label_items:
        category = str(item["category"])
        counts[category] = counts.get(category, 0) + 1
    family_rows = "\n".join(
        f"| {category} | {count} |" for category, count in sorted(counts.items())
    )
    return f"""# Complete Grammatical and Semantic Label Vocabulary

This is the exhaustive reference for the **{len(label_items)} fixed
grammatical and semantic labels** in tokenizer release `0.1.0-rc10`. The list
is generated directly from the released `tokens.txt`; the build fails if an
entry lacks a description. Token IDs are fixed for this release.

The release manifest historically calls a **{len(label_items) + len(lexical_items)}-entry**
block the “semantic token” region. That block also contains
**{len(lexical_items)} Tamil lexical components** used as secondary lemmas in
multi-lemma and auxiliary analyses. Those are content words, not semantic
labels, so they are not included in the label inventory below. Their fixed IDs
are {lexical_items[0]["id"]}–{lexical_items[-1]["id"]}; they remain in the
model vocabulary and are treated as lexical states by the word composer.

Structural codec markers, spelling choices, grapheme fallback, byte fallback,
and ordinary lemma-vocabulary entries are also outside this label inventory.

## Families

| Family | Entries |
| --- | ---: |
{family_rows}

## Complete inventory

{markdown_table(label_items)}

## Interpretation notes

- A `MORPH_...` entry is a normalized label inherited from an FST tag that
  has not yet been replaced by a narrower project-defined name. It is fixed
  in the release vocabulary and never created dynamically at runtime.
- Some broad verb labels remain available for exact raw-analysis inspection
  even when the canonical public stream omits them because a more specific
  feature already carries the same information.
- See `SEMANTIC_TOKENS.md` for worked Tamil examples and the public tokenizer
  contract for the distinction between semantic factors and reconstruction
  metadata.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    items = records()
    label_items = [item for item in items if str(item["token"]).startswith("<")]
    lexical_items = [item for item in items if not str(item["token"]).startswith("<")]
    if len(label_items) != 222 or len(lexical_items) != 62:
        raise RuntimeError(
            "Expected 222 grammatical/semantic labels and 62 lexical "
            f"components, found {len(label_items)} and {len(lexical_items)}"
        )
    payload = {
        "schema_version": "1.1.0",
        "tokenizer_version": "0.1.0-rc10",
        "count": len(label_items),
        "model_factor_region_count": len(items),
        "secondary_lexical_component_count": len(lexical_items),
        "secondary_lexical_components": lexical_items,
        "entries": label_items,
    }
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    doc_text = public_doc(label_items, lexical_items)

    if args.check:
        failures = []
        if not args.json.is_file() or args.json.read_text(encoding="utf-8") != json_text:
            failures.append(str(args.json))
        if not args.doc.is_file() or args.doc.read_text(encoding="utf-8") != doc_text:
            failures.append(str(args.doc))
        if failures:
            raise SystemExit("Semantic vocabulary references are stale: " + ", ".join(failures))
        return 0

    args.json.write_text(json_text, encoding="utf-8")
    args.doc.write_text(doc_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
