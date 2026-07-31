from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from collections import defaultdict

from .analysis import MorphAnalysis, parse_flookup_line

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_FST_DIR = PACKAGE_DIR / "data" / "fst-models"
DEFAULT_MODEL_ORDER = [
    "noun.fst",
    "pronoun.fst",
    "verb-c3.fst",
    "verb-c4.fst",
    "verb-c11.fst",
    "verb-c12.fst",
    "verb-c62.fst",
    "verb-c-rest.fst",
    "verb-auxiliary.fst",
    "adj.fst",
    "adv.fst",
    "part.fst",
]

@dataclass(frozen=True)
class FlookupResult:
    surface: str
    analyses: tuple[MorphAnalysis, ...]

class FlookupAnalyzer:
    def __init__(
        self,
        fst_dir: str | Path = DEFAULT_FST_DIR,
        model_names: list[str] | None = None,
        flookup_bin: str = "flookup",
    ) -> None:
        self.fst_dir = Path(fst_dir)
        self.model_names = model_names or DEFAULT_MODEL_ORDER
        self.flookup_bin = flookup_bin

    def available_models(self) -> list[Path]:
        return [self.fst_dir / name for name in self.model_names if (self.fst_dir / name).exists()]

    def ensure_ready(self) -> None:
        if shutil.which(self.flookup_bin) is None:
            raise RuntimeError(f"{self.flookup_bin!r} not found. Install foma/flookup first.")
        models = self.available_models()
        if not models:
            raise RuntimeError(f"No FST models found in {self.fst_dir}")

    def analyze(self, words: list[str]) -> dict[str, tuple[MorphAnalysis, ...]]:
        self.ensure_ready()
        grouped: dict[str, dict[str, MorphAnalysis]] = defaultdict(dict)
        unique_words = list(dict.fromkeys(words))
        payload = "\n".join(unique_words) + "\n"

        for model_path in self.available_models():
            proc = subprocess.run(
                [self.flookup_bin, str(model_path)],
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"flookup failed for {model_path.name}: {proc.stderr.strip() or proc.stdout.strip()}"
                )
            for line in proc.stdout.splitlines():
                parsed = parse_flookup_line(line, model=model_path.name)
                if parsed is None or not parsed.analysis.is_recognized:
                    continue
                existing = grouped[parsed.surface].get(parsed.analysis.raw)
                if existing is None:
                    grouped[parsed.surface][parsed.analysis.raw] = parsed.analysis
                    continue
                models = tuple(dict.fromkeys(filter(None, (existing.model, parsed.analysis.model))))
                grouped[parsed.surface][parsed.analysis.raw] = MorphAnalysis(
                    raw=existing.raw,
                    lemma=existing.lemma,
                    tags=existing.tags,
                    morph_tokens=existing.morph_tokens,
                    model="|".join(models) or None,
                )

        return {word: tuple(grouped.get(word, {}).values()) for word in words}
