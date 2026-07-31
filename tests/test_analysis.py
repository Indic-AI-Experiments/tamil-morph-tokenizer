from tamil_morph_tokenizer.analysis import (
    choose_best_analysis,
    parse_analysis,
    parse_flookup_line,
    tag_to_token,
)


def test_parse_noun_analysis():
    parsed = parse_flookup_line("மரங்களை\tமரம்+noun+pl+acc", model="noun.fst")
    assert parsed is not None
    assert parsed.surface == "மரங்களை"
    assert parsed.analysis.lemma == "மரம்"
    assert parsed.analysis.tags == ("noun", "pl", "acc")
    assert parsed.analysis.morph_tokens == ("<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>")


def test_parse_noun_compound_modifier_analysis():
    analysis = parse_analysis("உலகம்+noun+compoundmodifier")

    assert analysis.lemma == "உலகம்"
    assert analysis.morph_tokens == ("<POS_NOUN>", "<COMPOUND_MODIFIER>")


def test_parse_verb_analysis_with_realization_material():
    analysis = parse_analysis("படி+verb+fin+sim+strong+past=த்+3sgm=ஆன்", model="verb-c11.fst")
    assert analysis.lemma == "படி"
    assert "<POS_VERB>" not in analysis.morph_tokens
    assert "<VERB_FINITE>" not in analysis.morph_tokens
    assert "<VERB_STRONG>" not in analysis.morph_tokens
    assert "<TENSE_PAST>" in analysis.morph_tokens
    assert "<PERSON_3SG_MASC>" in analysis.morph_tokens


def test_parse_verbal_noun_uses_action_nominal_semantics():
    analysis = parse_analysis("தாக்கு+verb+nonfin+sim+verbalnoun=தல்")
    assert "<POS_VERB>" not in analysis.morph_tokens
    assert "<POS_VERBAL_NOUN>" in analysis.morph_tokens
    assert "<ACTION_NOMINAL>" in analysis.morph_tokens
    assert "<VERBAL_NOUN>" not in analysis.morph_tokens


def test_literal_auxiliary_value_emits_typed_link_and_lexical_lemma():
    analysis = parse_analysis("செய்+verb+nonfin+sim+neg=ஆ+aux=விடு+con=ஆல்")

    assert analysis.morph_tokens == (
        "<POLARITY_NEG>",
        "<LINK_VPART>",
        "விடு",
        "<MOOD_CONDITIONAL>",
    )
    assert "<AUXILIARY>" not in analysis.morph_tokens


def test_upstream_demonstrative_person_labels_are_contextually_corrected():
    analysis = parse_analysis("இவன்+pron+2sgm+dem+prox+nom")

    assert "<PERSON_3SG_MASC>" in analysis.morph_tokens
    assert "<PERSON_2SG_MASC>" not in analysis.morph_tokens


def test_final_closed_class_tags_have_specific_semantic_tokens():
    analysis = parse_analysis("கிமீ+abbrev+unit")
    assert analysis.morph_tokens == ("<ABBREVIATION>", "<MEASUREMENT_UNIT>")

    presentative = parse_analysis("இது+pron+dem+prox+3sgn+nom+presentative")
    assert "<PRESENTATIVE>" in presentative.morph_tokens

    interjection = parse_analysis("நன்றி+intj")
    assert interjection.morph_tokens == ("<POS_INTERJECTION>",)


def test_existential_polarity_tags_have_specific_semantic_tokens():
    positive = parse_analysis("பயன்+noun+exist+pos+adjpart=அ")
    negative = parse_analysis("தேவை+noun+exist+neg+adjpart=அ")
    assert "<POLARITY_POS>" in positive.morph_tokens
    assert "<POLARITY_NEG>" in negative.morph_tokens
    assert "<MORPH_POS>" not in positive.morph_tokens


def test_upstream_demonstrative_honorific_and_plural_are_third_person():
    honorific = parse_analysis("இவர்+pron+2sgh+dem+prox+nom")
    plural = parse_analysis("இவர்கள்+pron+2pl+dem+prox+nom")

    assert "<PERSON_3SG_HON>" in honorific.morph_tokens
    assert "<PERSON_2SG_HON>" not in honorific.morph_tokens
    assert "<PERSON_3PL>" in plural.morph_tokens
    assert "<PERSON_2PL>" not in plural.morph_tokens


def test_live_extended_tags_have_semantic_tokens():
    analysis = parse_analysis(
        "தன்+pron+3sg+refl+pssd+cardinal+ordinal+fraction+casemarker"
        "+caus+con+opt+infInc+PartNoun"
    )

    assert analysis.morph_tokens == (
        "<POS_PRONOUN>",
        "<PERSON_3SG>",
        "<PRON_REFLEXIVE>",
        "<PRON_POSSESSIVE>",
        "<NUM_CARDINAL>",
        "<NUM_ORDINAL>",
        "<NUM_FRACTION>",
        "<CASE_MARKER>",
        "<VOICE_CAUSATIVE>",
        "<MOOD_CONDITIONAL>",
        "<MOOD_OPTATIVE>",
        "<STEM_OBLIQUE>",
        "<POS_PARTICIPIAL_NOUN>",
    )


def test_choose_best_prefers_recognized_verb_over_unknown():
    unknown = parse_analysis("+?")
    verb = parse_analysis("படி+verb+fin+sim+strong+past=த்+3sgm=ஆன்")
    assert choose_best_analysis([unknown, verb]) == verb


def test_choose_best_prefers_standalone_noun_over_verbal_noun():
    noun = parse_analysis("தேர்தல்+noun+nom")
    verbal_noun = parse_analysis("தேர்+verb+nonfin+sim+verbalnoun=தல்")
    assert choose_best_analysis([verbal_noun, noun]) == noun


def test_choose_best_prefers_productive_negative_action_nominal_over_noun():
    noun = parse_analysis("செல்லாமை+noun+nom")
    verbal_noun = parse_analysis("செல்+verb+nonfin+sim+neg=ஆ+verbalnoun=மை")
    assert choose_best_analysis([noun, verbal_noun]) == verbal_noun


def test_choose_best_still_prefers_finite_verb_over_noun():
    noun = parse_analysis("படி+noun+nom")
    finite_verb = parse_analysis("படி+verb+fin+sim+pres=கிற்+3sgn=அது")
    assert choose_best_analysis([noun, finite_verb]) == finite_verb


def test_choose_best_prefers_lexical_noun_over_contextual_bare_imperative():
    noun = parse_analysis("கதை+noun+nom")
    imperative = parse_analysis("கதை+verb+fin+sim+imp=∅+2sg=∅")

    assert choose_best_analysis([imperative, noun]) == noun


def test_choose_best_prefers_lexical_intensifier_over_homographic_verb():
    verb = parse_analysis("ரொம்பு+verb+nonfin+sim+inf=அ")
    intensifier = parse_analysis("ரொம்ப+adv+intensifier")

    assert choose_best_analysis([verb, intensifier]) == intensifier


def test_choose_best_prefers_colloquial_vocative_over_homographic_imperative():
    imperative = parse_analysis("பா+verb+fin+sim+imp=∅+2sg=∅")
    vocative = parse_analysis("பா+intj+voc+colloq")

    assert choose_best_analysis([imperative, vocative]) == vocative


def test_choose_best_prefers_lexical_noun_over_participial_spelling_collision():
    noun = parse_analysis("அம்மி+noun+nom")
    participle = parse_analysis("அம்மு+verb+nonfin+sim+vpart=இ")

    assert choose_best_analysis([participle, noun]) == noun


def test_choose_best_prefers_noun_loc_over_abl_when_similar():
    loc = parse_analysis("காடு+noun+loc")
    abl = parse_analysis("காடு+noun+abl")
    assert choose_best_analysis([abl, loc]) == loc


def test_choose_best_prefers_modern_pronoun_genitive_over_traditional_ablative():
    gen = parse_analysis("அவர்+pron+dem+dist+3sgh+gen")
    abl = parse_analysis("அவர்+pron+dem+dist+3sgh+abl")
    assert choose_best_analysis([abl, gen]) == gen


def test_choose_best_prefers_noun_loc_over_soc_when_similar():
    loc = parse_analysis("புத்தகம்+noun+infInc+loc")
    soc = parse_analysis("புத்தகம்+noun+infInc+soc")
    assert choose_best_analysis([soc, loc]) == loc


def test_choose_best_prefers_additive_clausal_nominal_over_genitive_collision():
    noun = parse_analysis("சமைப்பு+noun+gen+add")
    verbal_noun = parse_analysis(
        "சமை+verb+nonfin+sim+verbalnoun=அது+add=உம்"
    )
    assert choose_best_analysis([noun, verbal_noun]) == verbal_noun


def test_choose_best_prefers_unmarked_action_nominal_over_future_variant():
    unmarked = parse_analysis(
        "ஒதுக்கிவிடு+verb+nonfin+complex+aspect+verbalnoun=அது"
    )
    future = parse_analysis(
        "ஒதுக்கிவிடு+verb+nonfin+complex+aspect+weak+fut=வ்+verbalnoun=அது"
    )

    assert choose_best_analysis([future, unmarked]) == unmarked


def test_choose_best_prefers_translative_over_ambiguous_become_infinitive():
    translative = parse_analysis("ரீதி+noun+trans+add=உம்")
    become = parse_analysis(
        "ரீதி+noun+verb+nonfin+complex+become+inf=அ+add=உம்"
    )
    assert choose_best_analysis([become, translative]) == translative


def test_choose_best_prefers_lexical_nominative_over_colloquial_translative_collision():
    translative = parse_analysis("அக்கு+noun+trans+colloq", model="noun.fst")
    nominative = parse_analysis("அக்கா+noun+nom", model="noun.fst")

    assert choose_best_analysis([translative, nominative]) == nominative


def test_choose_best_prefers_lexical_nominative_over_vocative_collision():
    vocative = parse_analysis("அக்கன்+noun+voc=ஏ+colloq", model="noun.fst")
    nominative = parse_analysis("அக்கா+noun+nom", model="noun.fst")

    assert choose_best_analysis([vocative, nominative]) == nominative


def test_productive_connector_tags_are_semantically_specific():
    assert tag_to_token("psp_padi") == "<POST_ACCORDING_TO>"
    assert tag_to_token("vpart_potu=போது") == "<TEMPORAL_WHEN>"
    assert tag_to_token("vpart_maaru=மாறு") == "<MANNER_PURPOSE>"
    assert tag_to_token("vpart_tum=தும்") == "<TEMPORAL_IMMEDIATE>"
    assert tag_to_token("recip") == "<RECIPROCAL>"
    assert tag_to_token("cond=இன்") == "<MOOD_CONDITIONAL>"
    assert tag_to_token("psp_ul") == "<POST_WITHIN_BY>"
