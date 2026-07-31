from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .analysis import MorphAnalysis, parse_analysis


ENTITY_TYPES = {
    "person",
    "country",
    "city",
    "region",
    "place",
    "org",
    "brand",
    "work",
    "other",
}
REVIEW_STATUSES = {"candidate", "reviewed", "rejected"}
ENTITY_DECLENSIONS = {
    "auto",
    "vowel_v",
    "vowel_y",
    "m_final",
    "u_drop",
    "du_geminate",
    "ru_geminate",
    "t_geminate",
    "k_geminate",
    "consonant",
    "indeclinable",
}
ENTITY_CASES = ("nom", "acc", "dat", "gen", "inst", "loc", "abl", "soc")
DEFAULT_ENTITY_GAZETTEER_PATH = Path(__file__).resolve().parent / "data/entities/tamil_geography.jsonl"
DEFAULT_REVIEWED_ENTITY_PATH = Path(__file__).resolve().parent / "data/entities/tamil_reviewed_entities.jsonl"
ENTITY_TOKENS = tuple(f"<ENTITY_{entity_type.upper()}>" for entity_type in sorted(ENTITY_TYPES))

VOWEL_V_ENDINGS = tuple("ாுூொோௌ") + ("ஆ", "உ", "ஊ", "ஒ", "ஓ", "ஔ")
VOWEL_Y_ENDINGS = tuple("ிீெேை") + ("இ", "ஈ", "எ", "ஏ", "ஐ")


@dataclass(frozen=True)
class EntityAlias:
    surface: str
    declension: str = "auto"


@dataclass(frozen=True)
class EntityEntry:
    lemma: str
    entity_type: str
    aliases: tuple[EntityAlias, ...]
    declension: str
    sources: tuple[str, ...]
    review_status: str
    entity_id: str | None = None
    blocked_surfaces: tuple[str, ...] = ()

    @property
    def name_forms(self) -> tuple[EntityAlias, ...]:
        return (EntityAlias(self.lemma, self.declension), *self.aliases)


@dataclass(frozen=True)
class EntitySurfaceMatch:
    entry: EntityEntry
    lemma: str
    case: str

    @property
    def analysis(self) -> MorphAnalysis:
        return parse_analysis(
            f"{self.lemma}+entity_{self.entry.entity_type}+{self.case}",
            model="entity-gazetteer",
        )


@dataclass(frozen=True)
class EntitySpanMatch:
    start: int
    end: int
    surface: str
    matches: tuple[EntitySurfaceMatch, ...]

    @property
    def analyses(self) -> tuple[MorphAnalysis, ...]:
        return tuple(match.analysis for match in self.matches)


def infer_declension(surface: str) -> str:
    final_word = surface.rsplit(" ", 1)[-1]
    if final_word.endswith("ம்"):
        return "m_final"
    if final_word.endswith(VOWEL_V_ENDINGS):
        return "vowel_v"
    if final_word.endswith(VOWEL_Y_ENDINGS):
        return "vowel_y"
    if final_word.endswith("்"):
        return "consonant"
    return "indeclinable"


def resolve_declension(surface: str, declension: str) -> str:
    if declension not in ENTITY_DECLENSIONS:
        raise ValueError(f"unsupported declension {declension!r}")
    return infer_declension(surface) if declension == "auto" else declension


def inflect_entity_form(surface: str, declension: str = "auto") -> dict[str, str]:
    """Return the conservative singular case paradigm for one attested name form."""

    resolved = resolve_declension(surface, declension)
    prefix, separator, final_word = surface.rpartition(" ")
    if not separator:
        final_word = surface
    if resolved == "indeclinable":
        final_forms = {"nom": final_word}
    elif resolved == "vowel_v":
        final_forms = {
            "nom": final_word,
            "acc": final_word + "வை",
            "dat": final_word + "வுக்கு",
            "gen": final_word + "வின்",
            "inst": final_word + "வால்",
            "loc": final_word + "வில்",
            "abl": final_word + "விலிருந்து",
            "soc": final_word + "வுடன்",
        }
    elif resolved == "vowel_y":
        final_forms = {
            "nom": final_word,
            "acc": final_word + "யை",
            "dat": final_word + "க்கு",
            "gen": final_word + "யின்",
            "inst": final_word + "யால்",
            "loc": final_word + "யில்",
            "abl": final_word + "யிலிருந்து",
            "soc": final_word + "யுடன்",
        }
    elif resolved == "m_final":
        stem = final_word.removesuffix("ம்")
        final_forms = {
            "nom": final_word,
            "acc": stem + "த்தை",
            "dat": stem + "த்துக்கு",
            "gen": stem + "த்தின்",
            "inst": stem + "த்தால்",
            "loc": stem + "த்தில்",
            "abl": stem + "த்திலிருந்து",
            "soc": stem + "த்துடன்",
        }
    elif resolved == "u_drop":
        if not final_word.endswith("ு"):
            raise ValueError(
                f"u_drop declension requires a short-u-final name: {surface!r}"
            )
        stem = final_word.removesuffix("ு")
        final_forms = {
            "nom": final_word,
            "acc": stem + "ை",
            "dat": stem + "ுக்கு",
            "gen": stem + "ின்",
            "inst": stem + "ால்",
            "loc": stem + "ில்",
            "abl": stem + "ிலிருந்து",
            "soc": stem + "ுடன்",
        }
    elif resolved in {"du_geminate", "ru_geminate"}:
        ending = "டு" if resolved == "du_geminate" else "று"
        strengthened = "ட்ட" if resolved == "du_geminate" else "ற்ற"
        if not final_word.endswith(ending):
            raise ValueError(
                f"{resolved} declension requires a {ending}-final name: {surface!r}"
            )
        stem = final_word.removesuffix(ending) + strengthened
        final_forms = {
            "nom": final_word,
            "acc": stem + "ை",
            "dat": stem + "ுக்கு",
            "gen": stem + "ின்",
            "inst": stem + "ால்",
            "loc": stem + "ில்",
            "abl": stem + "ிலிருந்து",
            "soc": stem + "ுடன்",
        }
    elif resolved in {"t_geminate", "k_geminate"}:
        ending = "த்" if resolved == "t_geminate" else "க்"
        strengthened = "த்த" if resolved == "t_geminate" else "க்க"
        if not final_word.endswith(ending):
            raise ValueError(
                f"{resolved} declension requires a {ending}-final name: {surface!r}"
            )
        stem = final_word.removesuffix(ending) + strengthened
        final_forms = {
            "nom": final_word,
            "acc": stem + "ை",
            "dat": stem + "ுக்கு",
            "gen": stem + "ின்",
            "inst": stem + "ால்",
            "loc": stem + "ில்",
            "abl": stem + "ிலிருந்து",
            "soc": stem + "ுடன்",
        }
    else:
        if not final_word.endswith("்"):
            raise ValueError(
                f"consonant declension requires a pulli-final name: {surface!r}"
            )
        stem = final_word.removesuffix("்")
        final_forms = {
            "nom": final_word,
            "acc": stem + "ை",
            "dat": stem + "ுக்கு",
            "gen": stem + "ின்",
            "inst": stem + "ால்",
            "loc": stem + "ில்",
            "abl": stem + "ிலிருந்து",
            "soc": stem + "ுடன்",
        }
    if not prefix:
        return final_forms
    return {case: f"{prefix} {form}" for case, form in final_forms.items()}


class EntityGazetteer:
    def __init__(self, entries: Iterable[EntityEntry] = ()) -> None:
        self.entries = tuple(entries)
        surface_index: dict[str, list[EntitySurfaceMatch]] = {}
        span_index: dict[tuple[str, ...], list[EntitySurfaceMatch]] = {}
        seen: set[tuple[str, str]] = set()
        for entry in self.entries:
            key = (entry.lemma, entry.entity_type)
            if key in seen:
                raise ValueError(f"Duplicate entity lemma/type: {key!r}")
            seen.add(key)
            if entry.review_status != "reviewed":
                continue
            seen_forms: set[str] = set()
            for name_form in entry.name_forms:
                if name_form.surface in seen_forms:
                    raise ValueError(
                        f"Duplicate name form for {entry.lemma!r}: {name_form.surface!r}"
                    )
                seen_forms.add(name_form.surface)
                for case, generated_surface in inflect_entity_form(
                    name_form.surface, name_form.declension
                ).items():
                    if generated_surface in entry.blocked_surfaces:
                        continue
                    match = EntitySurfaceMatch(entry, name_form.surface, case)
                    parts = tuple(generated_surface.split(" "))
                    if len(parts) == 1:
                        surface_index.setdefault(generated_surface, []).append(match)
                    else:
                        span_index.setdefault(parts, []).append(match)
        self._surface_index = {
            surface: tuple(matches) for surface, matches in surface_index.items()
        }
        self._span_index = {
            parts: tuple(matches) for parts, matches in span_index.items()
        }
        self._max_span_words = max((len(parts) for parts in span_index), default=1)
        form_declensions: dict[tuple[str, str], set[str]] = {}
        for entry in self.entries:
            if entry.review_status != "reviewed":
                continue
            for form in entry.name_forms:
                form_declensions.setdefault(
                    (form.surface, entry.entity_type), set()
                ).add(resolve_declension(form.surface, form.declension))
        self._form_declensions = {
            key: next(iter(values))
            for key, values in form_declensions.items()
            if len(values) == 1
        }

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "EntityGazetteer":
        entries: list[EntityEntry] = []
        with Path(path).open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                try:
                    payload = json.loads(line)
                    entries.append(parse_entity_entry(payload))
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid gazetteer row {line_number}: {exc}") from exc
        return cls(entries)

    def matches(self, surface: str) -> tuple[EntitySurfaceMatch, ...]:
        return self._surface_index.get(surface, ())

    def exact_matches(self, surface: str) -> tuple[EntityEntry, ...]:
        return tuple(
            dict.fromkeys(
                match.entry for match in self.matches(surface) if match.case == "nom"
            )
        )

    def longest_span(
        self, words: list[str], start: int
    ) -> EntitySpanMatch | None:
        upper = min(len(words), start + self._max_span_words)
        for end in range(upper, start + 1, -1):
            parts = tuple(words[start:end])
            matches = self._span_index.get(parts)
            if matches:
                return EntitySpanMatch(start, end, " ".join(parts), matches)
        return None

    def realize(self, lemma: str, entity_type: str, case: str) -> str | None:
        declension = self._form_declensions.get((lemma, entity_type))
        if declension is None:
            return None
        return inflect_entity_form(lemma, declension).get(case)


def required_string(payload: dict[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def string_list(payload: dict[str, object], name: str, *, required: bool) -> tuple[str, ...]:
    value = payload.get(name)
    if value is None and not required:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    result = tuple(dict.fromkeys(item.strip() for item in value))
    if required and not result:
        raise ValueError(f"{name} must not be empty")
    return result


def parse_aliases(payload: dict[str, object]) -> tuple[EntityAlias, ...]:
    value = payload.get("aliases", [])
    if not isinstance(value, list):
        raise ValueError("aliases must be a list")
    aliases: list[EntityAlias] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("each alias must be an object")
        surface = required_string(item, "surface")
        declension = required_string(item, "declension")
        resolve_declension(surface, declension)
        aliases.append(EntityAlias(surface, declension))
    if len({alias.surface for alias in aliases}) != len(aliases):
        raise ValueError("aliases must have unique surfaces")
    return tuple(aliases)


def parse_entity_entry(payload: object) -> EntityEntry:
    if not isinstance(payload, dict):
        raise TypeError("row must be an object")
    lemma = required_string(payload, "lemma")
    entity_type = required_string(payload, "entity_type")
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"unsupported entity_type {entity_type!r}")
    review_status = required_string(payload, "review_status")
    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"unsupported review_status {review_status!r}")
    aliases = parse_aliases(payload)
    if lemma in {alias.surface for alias in aliases}:
        raise ValueError("aliases must not repeat the canonical lemma")
    sources = string_list(payload, "sources", required=True)
    declension = required_string(payload, "declension")
    resolve_declension(lemma, declension)
    entity_id = payload.get("entity_id")
    if entity_id is not None and (not isinstance(entity_id, str) or not entity_id.strip()):
        raise ValueError("entity_id must be null or a non-empty string")
    blocked_surfaces = string_list(payload, "blocked_surfaces", required=False)
    possible_surfaces = {
        surface
        for form in (EntityAlias(lemma, declension), *aliases)
        for surface in inflect_entity_form(form.surface, form.declension).values()
    }
    if invalid := set(blocked_surfaces) - possible_surfaces:
        raise ValueError(f"blocked_surfaces are outside the entity paradigms: {sorted(invalid)!r}")
    return EntityEntry(
        lemma=lemma,
        entity_type=entity_type,
        aliases=aliases,
        declension=declension,
        sources=sources,
        review_status=review_status,
        entity_id=entity_id.strip() if isinstance(entity_id, str) else None,
        blocked_surfaces=blocked_surfaces,
    )


class EntityAnalyzer:
    """Analyze reviewed entity aliases and their conservative case paradigms."""

    def __init__(self, gazetteer: EntityGazetteer) -> None:
        self.gazetteer = gazetteer

    def analyze(self, words: list[str]) -> dict[str, tuple[MorphAnalysis, ...]]:
        return {
            word: tuple(match.analysis for match in self.gazetteer.matches(word))
            for word in words
        }

    def longest_span(self, words: list[str], start: int) -> EntitySpanMatch | None:
        return self.gazetteer.longest_span(words, start)

    def realize(self, lemma: str, entity_type: str, case: str) -> str | None:
        return self.gazetteer.realize(lemma, entity_type, case)


ExactEntityAnalyzer = EntityAnalyzer


@lru_cache(maxsize=1)
def default_entity_analyzer() -> EntityAnalyzer | None:
    if not DEFAULT_ENTITY_GAZETTEER_PATH.exists():
        return None
    manifest_path = DEFAULT_ENTITY_GAZETTEER_PATH.with_suffix(".manifest.json")
    if not manifest_path.exists():
        raise ValueError("Default entity gazetteer manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(DEFAULT_ENTITY_GAZETTEER_PATH.read_bytes()).hexdigest()
    if actual != manifest.get("gazetteer_sha256"):
        raise ValueError("Default entity gazetteer checksum does not match manifest")
    entries = list(EntityGazetteer.from_jsonl(DEFAULT_ENTITY_GAZETTEER_PATH).entries)
    if DEFAULT_REVIEWED_ENTITY_PATH.exists():
        reviewed_manifest_path = DEFAULT_REVIEWED_ENTITY_PATH.with_suffix(".manifest.json")
        if not reviewed_manifest_path.exists():
            raise ValueError("Reviewed entity supplement manifest is missing")
        reviewed_manifest = json.loads(reviewed_manifest_path.read_text(encoding="utf-8"))
        reviewed_actual = hashlib.sha256(DEFAULT_REVIEWED_ENTITY_PATH.read_bytes()).hexdigest()
        if reviewed_actual != reviewed_manifest.get("gazetteer_sha256"):
            raise ValueError("Reviewed entity supplement checksum does not match manifest")
        entries.extend(EntityGazetteer.from_jsonl(DEFAULT_REVIEWED_ENTITY_PATH).entries)
    return EntityAnalyzer(EntityGazetteer(entries))
