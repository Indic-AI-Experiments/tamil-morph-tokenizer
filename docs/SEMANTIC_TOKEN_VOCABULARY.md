# Complete Grammatical and Semantic Label Vocabulary

This is the exhaustive reference for the **222 fixed
grammatical and semantic labels** in tokenizer release `0.1.0-rc10`. The list
is generated directly from the released `tokens.txt`; the build fails if an
entry lacks a description. Token IDs are fixed for this release.

The release manifest historically calls a **284-entry**
block the “semantic token” region. That block also contains
**62 Tamil lexical components** used as secondary lemmas in
multi-lemma and auxiliary analyses. Those are content words, not semantic
labels, so they are not included in the label inventory below. Their fixed IDs
are 965–1026; they remain in the
model vocabulary and are treated as lexical states by the word composer.

Structural codec markers, spelling choices, grapheme fallback, byte fallback,
and ordinary lemma-vocabulary entries are also outside this label inventory.

## Families

| Family | Entries |
| --- | ---: |
| aspect | 2 |
| case | 11 |
| clitic | 2 |
| deixis | 9 |
| grammatical or semantic feature | 33 |
| legacy FST label | 22 |
| legacy postposition | 55 |
| legacy verbal relation | 8 |
| modality | 3 |
| mood | 5 |
| named entity | 9 |
| number and quantity | 5 |
| part of speech | 9 |
| participle | 3 |
| person and agreement | 15 |
| polarity | 2 |
| postposition and relation | 10 |
| pronoun | 4 |
| sandhi | 4 |
| tense | 3 |
| verb form | 6 |
| voice | 2 |

## Complete inventory

| ID | Token | Family | Meaning | Source |
| ---: | --- | --- | --- | --- |
| 743 | `<ABBREVIATION>` | grammatical or semantic feature | Marks an abbreviation. | mapped FST tag or reviewed semantic mapping |
| 744 | `<ACTION_NOMINAL>` | grammatical or semantic feature | Marks a verb-derived noun that names an action or event. | project semantic mapping |
| 745 | `<ADJECTIVAL_PARTICIPLE>` | participle | Marks a verb form used to modify a noun. | mapped FST tag or reviewed semantic mapping |
| 746 | `<ASPECT_PERFECT>` | aspect | Marks a completed action or a resulting state. | mapped FST tag or reviewed semantic mapping |
| 747 | `<ASPECT_PROSPECTIVE>` | aspect | Marks an action viewed as expected or about to happen. | mapped FST tag or reviewed semantic mapping |
| 748 | `<AUX_ATTITUDINAL>` | grammatical or semantic feature | Broad inherited FST label for an auxiliary construction that expresses the speaker's stance. | mapped FST tag or reviewed semantic mapping |
| 749 | `<CASE_ABL>` | case | Ablative case: from, out of, or away from. | mapped FST tag or reviewed semantic mapping |
| 750 | `<CASE_ACC>` | case | Accusative case: usually the direct object. | mapped FST tag or reviewed semantic mapping |
| 751 | `<CASE_DAT>` | case | Dative case: usually to or for. | mapped FST tag or reviewed semantic mapping |
| 752 | `<CASE_GEN>` | case | Genitive case: possession or an of-relation. | mapped FST tag or reviewed semantic mapping |
| 753 | `<CASE_INST>` | case | Instrumental case: by, with, or using. | mapped FST tag or reviewed semantic mapping |
| 754 | `<CASE_LOC>` | case | Locative case: in, at, or on. | mapped FST tag or reviewed semantic mapping |
| 755 | `<CASE_MARKER>` | case | Broad inherited FST label indicating that a case marker is present. | mapped FST tag or reviewed semantic mapping |
| 756 | `<CASE_NOM>` | case | Nominative or unmarked base case, often used for the subject. | mapped FST tag or reviewed semantic mapping |
| 757 | `<CASE_SOC>` | case | Sociative case: with or together with. | mapped FST tag or reviewed semantic mapping |
| 758 | `<CASE_TRANS>` | case | Translative or adverbial case-like form: as, becoming, or in a stated manner. | mapped FST tag or reviewed semantic mapping |
| 759 | `<CASE_VOC>` | case | Vocative case used for direct address. | mapped FST tag or reviewed semantic mapping |
| 760 | `<CLITIC_ADD>` | clitic | Additive clitic: also, too, or and. | mapped FST tag or reviewed semantic mapping |
| 761 | `<CLITIC_FOCUS>` | clitic | Focus or emphatic clitic, often corresponding to தான். | mapped FST tag or reviewed semantic mapping |
| 762 | `<COMPARATIVE>` | grammatical or semantic feature | Marks a comparison such as than, more, or less. | mapped FST tag or reviewed semantic mapping |
| 763 | `<COMPLEMENTIZER>` | grammatical or semantic feature | Introduces a quoted, reported, or embedded clause. | mapped FST tag or reviewed semantic mapping |
| 764 | `<COMPOUND_MODIFIER>` | grammatical or semantic feature | Marks a noun used attributively before another word in a compound. | mapped FST tag or reviewed semantic mapping |
| 765 | `<COPULA>` | grammatical or semantic feature | Marks a copular expression that links a subject with a description or identity. | mapped FST tag or reviewed semantic mapping |
| 766 | `<COP_BECOME>` | grammatical or semantic feature | Marks a change into a state: become. | project semantic mapping |
| 767 | `<DEGREE>` | grammatical or semantic feature | Marks an amount or degree expression. | mapped FST tag or reviewed semantic mapping |
| 768 | `<DEICTIC>` | deixis | General demonstrative or pointing meaning. | mapped FST tag or reviewed semantic mapping |
| 769 | `<DEICTIC_DIST>` | deixis | Distal demonstrative: that, there, or then. | mapped FST tag or reviewed semantic mapping |
| 770 | `<DEICTIC_INTERROGATIVE>` | deixis | Interrogative demonstrative: which, where, or when. | mapped FST tag or reviewed semantic mapping |
| 771 | `<DEICTIC_MED>` | deixis | Medial demonstrative: an intermediate distance. | mapped FST tag or reviewed semantic mapping |
| 772 | `<DEICTIC_PROX>` | deixis | Proximal demonstrative: this, here, or now. | mapped FST tag or reviewed semantic mapping |
| 773 | `<DEICTIC_SAME>` | deixis | Marks identity or sameness: the same. | mapped FST tag or reviewed semantic mapping |
| 774 | `<DEICTIC_SITUATION>` | deixis | Points to a situation or context. | mapped FST tag or reviewed semantic mapping |
| 775 | `<DEICTIC_TIME>` | deixis | Points to a time. | mapped FST tag or reviewed semantic mapping |
| 776 | `<DEICTIC_TYPE>` | deixis | Points to a kind or type. | mapped FST tag or reviewed semantic mapping |
| 777 | `<DERIV_AATTAM>` | grammatical or semantic feature | Marks the ஆட்டம்-derived manner or likeness construction. | mapped FST tag or reviewed semantic mapping |
| 778 | `<DETERMINER>` | grammatical or semantic feature | Marks a word that specifies or limits a noun. | mapped FST tag or reviewed semantic mapping |
| 779 | `<DISTRIBUTIVE>` | grammatical or semantic feature | Distributive meaning: each, respective, or one by one. | mapped FST tag or reviewed semantic mapping |
| 780 | `<ENTITY_BRAND>` | named entity | Named entity: brand. | mapped FST tag or reviewed semantic mapping |
| 781 | `<ENTITY_CITY>` | named entity | Named entity: city. | mapped FST tag or reviewed semantic mapping |
| 782 | `<ENTITY_COUNTRY>` | named entity | Named entity: country. | mapped FST tag or reviewed semantic mapping |
| 783 | `<ENTITY_ORG>` | named entity | Named entity: organization. | mapped FST tag or reviewed semantic mapping |
| 784 | `<ENTITY_OTHER>` | named entity | Named entity: other reviewed entity type. | mapped FST tag or reviewed semantic mapping |
| 785 | `<ENTITY_PERSON>` | named entity | Named entity: person. | mapped FST tag or reviewed semantic mapping |
| 786 | `<ENTITY_PLACE>` | named entity | Named entity: place. | mapped FST tag or reviewed semantic mapping |
| 787 | `<ENTITY_REGION>` | named entity | Named entity: region. | mapped FST tag or reviewed semantic mapping |
| 788 | `<ENTITY_WORK>` | named entity | Named entity: named creative work. | mapped FST tag or reviewed semantic mapping |
| 789 | `<EUPHONIC_AUGMENT>` | grammatical or semantic feature | Marks an inserted sound used to join morphemes smoothly. | mapped FST tag or reviewed semantic mapping |
| 790 | `<EVIDENTIAL_REPORTATIVE>` | grammatical or semantic feature | Marks information presented as reported rather than directly witnessed. | mapped FST tag or reviewed semantic mapping |
| 791 | `<EXISTENTIAL>` | grammatical or semantic feature | Marks existence or availability. | mapped FST tag or reviewed semantic mapping |
| 792 | `<FUTURE_ADJECTIVAL_PARTICIPLE>` | participle | Marks a future-oriented verb form used to modify a noun. | mapped FST tag or reviewed semantic mapping |
| 793 | `<INDEFINITE>` | grammatical or semantic feature | Marks an indefinite meaning such as some or any. | mapped FST tag or reviewed semantic mapping |
| 794 | `<LETTER_NAME>` | grammatical or semantic feature | Marks a spoken or written letter name. | mapped FST tag or reviewed semantic mapping |
| 795 | `<MANNER_PURPOSE>` | grammatical or semantic feature | Marks a directed manner or intended outcome, often in -உமாறு. | mapped FST tag or reviewed semantic mapping |
| 796 | `<MEASUREMENT_UNIT>` | grammatical or semantic feature | Marks a unit of measurement. | mapped FST tag or reviewed semantic mapping |
| 797 | `<MODAL>` | modality | Broad modal meaning such as ability, necessity, or possibility. | mapped FST tag or reviewed semantic mapping |
| 798 | `<MODAL_MUST>` | modality | Necessity or obligation: must, should, or need to. | reviewed lexical special or FST mapping |
| 799 | `<MODAL_WORTHY>` | modality | Marks suitability or worthiness. | mapped FST tag or reviewed semantic mapping |
| 800 | `<MOOD_CONDITIONAL>` | mood | Conditional mood: if or under a condition. | mapped FST tag or reviewed semantic mapping |
| 801 | `<MOOD_OPTATIVE>` | mood | Optative mood: a wish, hope, or blessing. | mapped FST tag or reviewed semantic mapping |
| 802 | `<MOOD_PARTICLE>` | mood | Marks a particle that contributes mood. | mapped FST tag or reviewed semantic mapping |
| 803 | `<MOOD_PROHIBITIVE>` | mood | Negative command: do not. | mapped FST tag or reviewed semantic mapping |
| 804 | `<MOOD_QUESTION>` | mood | Marks a question. | mapped FST tag or reviewed semantic mapping |
| 805 | `<MORPH_AFFIRM>` | legacy FST label | Legacy FST label for affirmative meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 806 | `<MORPH_ALT>` | legacy FST label | Legacy FST label for alternative form or reading; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 807 | `<MORPH_BEN>` | legacy FST label | Legacy FST label for benefactive meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 808 | `<MORPH_CMPR>` | legacy FST label | Legacy FST label for comparative meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 809 | `<MORPH_CONJUNCTION>` | legacy FST label | Legacy FST label for conjunction; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 810 | `<MORPH_DEICTIC>` | legacy FST label | Legacy FST label for deictic or demonstrative meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 811 | `<MORPH_EXCLAM>` | legacy FST label | Legacy FST label for exclamation; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 812 | `<MORPH_INT>` | legacy FST label | Legacy FST label for intensifying or interrogative legacy label; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 813 | `<MORPH_INTERJECTION>` | legacy FST label | Legacy FST label for interjection; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 814 | `<MORPH_INTERROGATIVE>` | legacy FST label | Legacy FST label for interrogative meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 815 | `<MORPH_LIMIT>` | legacy FST label | Legacy FST label for limit or restriction; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 816 | `<MORPH_LOAN>` | legacy FST label | Legacy FST label for loanword; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 817 | `<MORPH_NEUT>` | legacy FST label | Legacy FST label for neuter agreement or class; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 818 | `<MORPH_N_PATHIL>` | legacy FST label | Legacy FST label for noun-based பதில் relational construction; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 819 | `<MORPH_OTHER>` | legacy FST label | Legacy FST label for other inherited FST category; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 820 | `<MORPH_PRIV>` | legacy FST label | Legacy FST label for privative meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 821 | `<MORPH_PSP_ALLAAMAL>` | legacy postposition | Legacy FST postposition label meaning without. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 822 | `<MORPH_PSP_APPAAL>` | legacy postposition | Legacy FST postposition label meaning beyond or on the other side. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 823 | `<MORPH_PSP_APPAAL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from beyond or on the other side. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 824 | `<MORPH_PSP_APPURAM>` | legacy postposition | Legacy FST postposition label meaning after. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 825 | `<MORPH_PSP_ARUKIL>` | legacy postposition | Legacy FST postposition label meaning near. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 826 | `<MORPH_PSP_ARUKIL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from near. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 827 | `<MORPH_PSP_ATIYIL>` | legacy postposition | Legacy FST postposition label meaning under or at the foot of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 828 | `<MORPH_PSP_ATIYIL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from under or at the foot of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 829 | `<MORPH_PSP_ETHIR>` | legacy postposition | Legacy FST postposition label meaning opposite or against. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 830 | `<MORPH_PSP_ETHIRE>` | legacy postposition | Legacy FST postposition label meaning opposite or facing. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 831 | `<MORPH_PSP_ETHIRE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from opposite or facing. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 832 | `<MORPH_PSP_ETHIR_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from opposite or against. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 833 | `<MORPH_PSP_IDAIYIL>` | legacy postposition | Legacy FST postposition label meaning between or among. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 834 | `<MORPH_PSP_IDAIYL>` | legacy postposition | Legacy FST postposition label meaning between or among. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 835 | `<MORPH_PSP_IDAYIL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from between or among. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 836 | `<MORPH_PSP_ILLAAMAL>` | legacy postposition | Legacy FST postposition label meaning without. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 837 | `<MORPH_PSP_KEEL>` | legacy postposition | Legacy FST postposition label meaning below. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 838 | `<MORPH_PSP_KEELE>` | legacy postposition | Legacy FST postposition label meaning below. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 839 | `<MORPH_PSP_KEELE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from below. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 840 | `<MORPH_PSP_KEEL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from below. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 841 | `<MORPH_PSP_KURUKKE>` | legacy postposition | Legacy FST postposition label meaning across. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 842 | `<MORPH_PSP_KURUKKE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from across. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 843 | `<MORPH_PSP_MEEL>` | legacy postposition | Legacy FST postposition label meaning above or on. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 844 | `<MORPH_PSP_MEELE>` | legacy postposition | Legacy FST postposition label meaning above or on. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 845 | `<MORPH_PSP_MEELE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from above or on. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 846 | `<MORPH_PSP_MEEL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from above or on. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 847 | `<MORPH_PSP_MUN>` | legacy postposition | Legacy FST postposition label meaning before or in front of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 848 | `<MORPH_PSP_MUNNAAL>` | legacy postposition | Legacy FST postposition label meaning before. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 849 | `<MORPH_PSP_MUNNAAL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from before. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 850 | `<MORPH_PSP_MUNNE>` | legacy postposition | Legacy FST postposition label meaning before or in front. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 851 | `<MORPH_PSP_MUN_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from before or in front of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 852 | `<MORPH_PSP_NADUVIL>` | legacy postposition | Legacy FST postposition label meaning in the middle of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 853 | `<MORPH_PSP_NADUVIL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from in the middle of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 854 | `<MORPH_PSP_PIN>` | legacy postposition | Legacy FST postposition label meaning after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 855 | `<MORPH_PSP_PINNAAL>` | legacy postposition | Legacy FST postposition label meaning after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 856 | `<MORPH_PSP_PINNAAL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 857 | `<MORPH_PSP_PINNE>` | legacy postposition | Legacy FST postposition label meaning after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 858 | `<MORPH_PSP_PINNE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 859 | `<MORPH_PSP_PIN_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from after or behind. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 860 | `<MORPH_PSP_PIRAKU>` | legacy postposition | Legacy FST postposition label meaning after. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 861 | `<MORPH_PSP_POL>` | legacy postposition | Legacy FST postposition label meaning like or as. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 862 | `<MORPH_PSP_POLA>` | legacy postposition | Legacy FST postposition label meaning like or as. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 863 | `<MORPH_PSP_TAVIRA>` | legacy postposition | Legacy FST postposition label meaning except. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 864 | `<MORPH_PSP_ULE>` | legacy postposition | Legacy FST postposition label meaning inside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 865 | `<MORPH_PSP_ULE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from inside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 866 | `<MORPH_PSP_ULLE>` | legacy postposition | Legacy FST postposition label meaning inside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 867 | `<MORPH_PSP_ULLE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from inside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 868 | `<MORPH_PSP_UL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from inside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 869 | `<MORPH_PSP_VALIYAAKA>` | legacy postposition | Legacy FST postposition label meaning through or by way of. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 870 | `<MORPH_PSP_VARAIKKUM>` | legacy postposition | Legacy FST postposition label meaning until or up to. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 871 | `<MORPH_PSP_VARAIYIL>` | legacy postposition | Legacy FST postposition label meaning until or within the limit. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 872 | `<MORPH_PSP_VELIYEE>` | legacy postposition | Legacy FST postposition label meaning outside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 873 | `<MORPH_PSP_VELIYEE_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from outside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 874 | `<MORPH_PSP_VELIYIL>` | legacy postposition | Legacy FST postposition label meaning outside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 875 | `<MORPH_PSP_VELIYIL_IRUNTU>` | legacy postposition | Legacy FST postposition label meaning from outside. It remains fixed in the released vocabulary pending a narrower named mapping. | normalized inherited FST tag |
| 876 | `<MORPH_REGISTER>` | legacy FST label | Legacy FST label for register label; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 877 | `<MORPH_SANDHI_C>` | legacy FST label | Legacy FST label for legacy c-type sandhi; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 878 | `<MORPH_SANDHI_K>` | legacy FST label | Legacy FST label for legacy k-type sandhi; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 879 | `<MORPH_SANDHI_P>` | legacy FST label | Legacy FST label for legacy p-type sandhi; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 880 | `<MORPH_SANDHI_T>` | legacy FST label | Legacy FST label for legacy t-type sandhi; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 881 | `<MORPH_UNTIL>` | legacy FST label | Legacy FST label for until or boundary meaning; retained as a fixed readable factor rather than created dynamically. | normalized inherited FST tag |
| 882 | `<MORPH_VPARTP_TAANDI>` | legacy verbal relation | Legacy participial relation meaning beyond or crossing. | normalized inherited FST tag |
| 883 | `<MORPH_VPART_CUTTI>` | legacy verbal relation | Legacy verbal-participle relation meaning around or concerning. | normalized inherited FST tag |
| 884 | `<MORPH_VPART_KONDU>` | legacy verbal relation | Legacy verbal-participle relation meaning with, by, or while doing. | normalized inherited FST tag |
| 885 | `<MORPH_VPART_OTTI>` | legacy verbal relation | Legacy verbal-participle relation meaning adjoining or in relation to. | normalized inherited FST tag |
| 886 | `<MORPH_VPART_TAANDI>` | legacy verbal relation | Legacy verbal-participle relation meaning beyond or crossing. | normalized inherited FST tag |
| 887 | `<MORPH_VPART_TAVIRTU>` | legacy verbal relation | Legacy verbal-participle relation meaning excluding or avoiding. | normalized inherited FST tag |
| 888 | `<MORPH_VPART_VAITTU>` | legacy verbal relation | Legacy verbal-participle relation meaning using, keeping, or having done. | normalized inherited FST tag |
| 889 | `<MORPH_VPART_VIDA>` | legacy verbal relation | Legacy verbal-participle relation meaning than or leaving. | normalized inherited FST tag |
| 890 | `<NEGATIVE_PARTICIPLE>` | participle | Marks a negative non-finite or modifying verb form. | mapped FST tag or reviewed semantic mapping |
| 891 | `<NUM_CARDINAL>` | number and quantity | Cardinal number: one, two, three, and so on. | mapped FST tag or reviewed semantic mapping |
| 892 | `<NUM_FRACTION>` | number and quantity | Fractional number. | mapped FST tag or reviewed semantic mapping |
| 893 | `<NUM_ORDINAL>` | number and quantity | Ordinal number: first, second, and so on. | mapped FST tag or reviewed semantic mapping |
| 894 | `<NUM_PL>` | number and quantity | Plural number. | mapped FST tag or reviewed semantic mapping |
| 895 | `<NUM_SG>` | number and quantity | Singular number. | mapped FST tag or reviewed semantic mapping |
| 896 | `<PART_ONLY>` | grammatical or semantic feature | Restrictive particle: only or just. | reviewed lexical special or FST mapping |
| 897 | `<PERSON_1PL>` | person and agreement | First person plural: we. | mapped FST tag or reviewed semantic mapping |
| 898 | `<PERSON_1SG>` | person and agreement | First person singular: I. | mapped FST tag or reviewed semantic mapping |
| 899 | `<PERSON_2PL>` | person and agreement | Second person plural: you (plural). | mapped FST tag or reviewed semantic mapping |
| 900 | `<PERSON_2PL_HON>` | person and agreement | Second person plural honorific: respectful you. | mapped FST tag or reviewed semantic mapping |
| 901 | `<PERSON_2SG>` | person and agreement | Second person singular: you. | mapped FST tag or reviewed semantic mapping |
| 902 | `<PERSON_2SG_HON>` | person and agreement | Second person singular honorific: respectful you. | mapped FST tag or reviewed semantic mapping |
| 903 | `<PERSON_3PL>` | person and agreement | Third person plural: they. | mapped FST tag or reviewed semantic mapping |
| 904 | `<PERSON_3PL_EPICENE>` | person and agreement | Third person plural without a masculine/feminine distinction. | mapped FST tag or reviewed semantic mapping |
| 905 | `<PERSON_3PL_NEUT>` | person and agreement | Third person plural neuter or non-human. | mapped FST tag or reviewed semantic mapping |
| 906 | `<PERSON_3SG>` | person and agreement | Third person singular. | mapped FST tag or reviewed semantic mapping |
| 907 | `<PERSON_3SG_EPICENE>` | person and agreement | Third person singular without a masculine/feminine distinction. | mapped FST tag or reviewed semantic mapping |
| 908 | `<PERSON_3SG_FEM>` | person and agreement | Third person singular feminine: she. | mapped FST tag or reviewed semantic mapping |
| 909 | `<PERSON_3SG_HON>` | person and agreement | Third person singular honorific. | mapped FST tag or reviewed semantic mapping |
| 910 | `<PERSON_3SG_MASC>` | person and agreement | Third person singular masculine: he. | mapped FST tag or reviewed semantic mapping |
| 911 | `<PERSON_3SG_NEUT>` | person and agreement | Third person singular neuter: it. | mapped FST tag or reviewed semantic mapping |
| 912 | `<POLARITY_NEG>` | polarity | Negative polarity. | mapped FST tag or reviewed semantic mapping |
| 913 | `<POLARITY_POS>` | polarity | Positive polarity. | mapped FST tag or reviewed semantic mapping |
| 914 | `<POSTPOSITION>` | postposition and relation | General postposition or relational function word. | mapped FST tag or reviewed semantic mapping |
| 915 | `<POST_ABOUT>` | postposition and relation | Relation meaning about or concerning. | mapped FST tag or reviewed semantic mapping |
| 916 | `<POST_ACCORDING_TO>` | postposition and relation | Relation meaning according to or in the manner stated. | mapped FST tag or reviewed semantic mapping |
| 917 | `<POST_AFTER>` | postposition and relation | Temporal or spatial relation meaning after or behind. | mapped FST tag or reviewed semantic mapping |
| 918 | `<POST_AMONG>` | postposition and relation | Relation meaning among or between. | mapped FST tag or reviewed semantic mapping |
| 919 | `<POST_BEFORE>` | postposition and relation | Temporal or spatial relation meaning before or in front of. | reviewed lexical special or FST mapping |
| 920 | `<POST_LIKE_AS>` | postposition and relation | Similarity relation: like or as. | mapped FST tag or reviewed semantic mapping |
| 921 | `<POST_TOWARD>` | postposition and relation | Direction relation: toward. | mapped FST tag or reviewed semantic mapping |
| 922 | `<POST_UNTIL>` | postposition and relation | Boundary relation: until or up to. | reviewed lexical special or FST mapping |
| 923 | `<POST_WITHIN_BY>` | postposition and relation | Interior or deadline relation: within, inside, or by. | mapped FST tag or reviewed semantic mapping |
| 924 | `<POS_ADJ>` | part of speech | Part of speech: adjective. | mapped FST tag or reviewed semantic mapping |
| 925 | `<POS_ADV>` | part of speech | Part of speech: adverb. | mapped FST tag or reviewed semantic mapping |
| 926 | `<POS_INTERJECTION>` | part of speech | Part of speech: interjection. | mapped FST tag or reviewed semantic mapping |
| 927 | `<POS_NOUN>` | part of speech | Part of speech: noun. | mapped FST tag or reviewed semantic mapping |
| 928 | `<POS_PART>` | part of speech | Part of speech: particle. | mapped FST tag or reviewed semantic mapping |
| 929 | `<POS_PARTICIPIAL_NOUN>` | part of speech | Part of speech: noun formed from a participle. | mapped FST tag or reviewed semantic mapping |
| 930 | `<POS_PRONOUN>` | part of speech | Part of speech: pronoun. | mapped FST tag or reviewed semantic mapping |
| 931 | `<POS_QUANTIFIER>` | part of speech | Part of speech: quantifier. | mapped FST tag or reviewed semantic mapping |
| 932 | `<POS_VERBAL_NOUN>` | part of speech | Part of speech: verb-derived action or event noun. | mapped FST tag or reviewed semantic mapping |
| 933 | `<PRESENTATIVE>` | grammatical or semantic feature | Presentative expression used to point out or introduce something. | mapped FST tag or reviewed semantic mapping |
| 934 | `<PRIVATIVE_WITHOUT>` | grammatical or semantic feature | Privative meaning: without or lacking. | mapped FST tag or reviewed semantic mapping |
| 935 | `<PRON_EXCLUSIVE>` | pronoun | Exclusive first-person plural: we, excluding the addressee. | mapped FST tag or reviewed semantic mapping |
| 936 | `<PRON_INCLUSIVE>` | pronoun | Inclusive first-person plural: we, including the addressee. | mapped FST tag or reviewed semantic mapping |
| 937 | `<PRON_POSSESSIVE>` | pronoun | Possessive pronoun function. | mapped FST tag or reviewed semantic mapping |
| 938 | `<PRON_REFLEXIVE>` | pronoun | Reflexive pronoun function: self. | mapped FST tag or reviewed semantic mapping |
| 939 | `<QUANT_ALL>` | grammatical or semantic feature | Universal quantity: all or every. | mapped FST tag or reviewed semantic mapping |
| 940 | `<RECIPROCAL>` | grammatical or semantic feature | Reciprocal relation: each other. | mapped FST tag or reviewed semantic mapping |
| 941 | `<REDUPLICATION>` | grammatical or semantic feature | Marks a repeated form used for distribution, emphasis, or iteration. | mapped FST tag or reviewed semantic mapping |
| 942 | `<REGISTER_COLLOQUIAL>` | grammatical or semantic feature | Marks a colloquial form. | mapped FST tag or reviewed semantic mapping |
| 943 | `<REL_ATTACH>` | grammatical or semantic feature | Marks an attaching or related-to construction. | mapped FST tag or reviewed semantic mapping |
| 944 | `<SANDHI_C>` | sandhi | Marks c-type linking sandhi. | mapped FST tag or reviewed semantic mapping |
| 945 | `<SANDHI_K>` | sandhi | Marks k-type linking sandhi. | mapped FST tag or reviewed semantic mapping |
| 946 | `<SANDHI_P>` | sandhi | Marks p-type linking sandhi. | mapped FST tag or reviewed semantic mapping |
| 947 | `<SANDHI_T>` | sandhi | Marks t-type linking sandhi. | mapped FST tag or reviewed semantic mapping |
| 948 | `<SEM_HUMAN>` | grammatical or semantic feature | Marks reference to a human being or group. | project semantic mapping |
| 949 | `<SEM_PURPOSE>` | grammatical or semantic feature | Marks purpose or intended use. | project semantic mapping |
| 950 | `<STEM_OBLIQUE>` | grammatical or semantic feature | Marks a changed noun stem used before a case ending. | mapped FST tag or reviewed semantic mapping |
| 951 | `<TEMPORAL_IMMEDIATE>` | grammatical or semantic feature | Marks immediate succession: as soon as. | mapped FST tag or reviewed semantic mapping |
| 952 | `<TEMPORAL_WHEN>` | grammatical or semantic feature | Marks a time relation: when or while. | mapped FST tag or reviewed semantic mapping |
| 953 | `<TENSE_FUTURE>` | tense | Future tense. | mapped FST tag or reviewed semantic mapping |
| 954 | `<TENSE_PAST>` | tense | Past tense. | mapped FST tag or reviewed semantic mapping |
| 955 | `<TENSE_PRESENT>` | tense | Present tense. | mapped FST tag or reviewed semantic mapping |
| 956 | `<TITLE_HONORIFIC>` | grammatical or semantic feature | Marks an honorific title. | mapped FST tag or reviewed semantic mapping |
| 957 | `<VERBAL_PARTICIPLE>` | verb form | Marks a non-finite verb that links to a following action. | mapped FST tag or reviewed semantic mapping |
| 958 | `<VERB_COMPLEX>` | verb form | Broad inherited FST label for a complex verb construction. | mapped FST tag or reviewed semantic mapping |
| 959 | `<VERB_FINITE>` | verb form | Broad inherited FST label for a finite verb. | mapped FST tag or reviewed semantic mapping |
| 960 | `<VERB_IMPERATIVE>` | verb form | Imperative verb form: a command or request. | mapped FST tag or reviewed semantic mapping |
| 961 | `<VERB_INFINITIVE>` | verb form | Infinitive verb form. | mapped FST tag or reviewed semantic mapping |
| 962 | `<VERB_NONFINITE>` | verb form | Broad inherited FST label for a non-finite verb. | mapped FST tag or reviewed semantic mapping |
| 963 | `<VOICE_CAUSATIVE>` | voice | Causative voice: causes someone or something to act. | mapped FST tag or reviewed semantic mapping |
| 964 | `<VOICE_PASSIVE>` | voice | Passive voice: presents the affected participant rather than the actor. | mapped FST tag or reviewed semantic mapping |

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
