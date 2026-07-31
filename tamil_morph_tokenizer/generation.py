from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from .analysis import MorphAnalysis
from .fst import DEFAULT_FST_DIR, DEFAULT_MODEL_ORDER


class FlookupGenerator:
    """Inverse-generate exact surfaces for an existing raw FST analysis."""

    def __init__(
        self,
        fst_dir: str | Path = DEFAULT_FST_DIR,
        model_names: list[str] | None = None,
        flookup_bin: str = "flookup",
    ) -> None:
        self.fst_dir = Path(fst_dir)
        self.model_names = model_names or DEFAULT_MODEL_ORDER
        self.flookup_bin = flookup_bin
        self._cache: dict[tuple[str, str | None], tuple[str, ...]] = {}

    def ensure_ready(self) -> None:
        if shutil.which(self.flookup_bin) is None:
            raise RuntimeError(f"{self.flookup_bin!r} not found. Install foma/flookup first.")
        if not self.available_models():
            raise RuntimeError(f"No FST models found in {self.fst_dir}")

    def available_models(self) -> tuple[str, ...]:
        return tuple(
            name for name in self.model_names
            if (self.fst_dir / name).exists()
        )

    def models_for_analysis(self, analysis: MorphAnalysis) -> tuple[str, ...]:
        available = set(self.available_models())
        if analysis.model:
            selected = tuple(
                model for model in analysis.model.split("|")
                if model in available
            )
            if selected:
                return selected
        return tuple(name for name in self.model_names if name in available)

    def generate(self, analysis: MorphAnalysis) -> tuple[str, ...]:
        if not analysis.is_recognized:
            return ()
        cache_key = (analysis.raw, analysis.model)
        if cache_key in self._cache:
            return self._cache[cache_key]
        self.ensure_ready()
        surfaces: set[str] = set()
        payload = analysis.raw + "\n"
        for model_name in self.models_for_analysis(analysis):
            proc = subprocess.run(
                [self.flookup_bin, "-i", str(self.fst_dir / model_name)],
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"inverse flookup failed for {model_name}: "
                    f"{proc.stderr.strip() or proc.stdout.strip()}"
                )
            for line in proc.stdout.splitlines():
                if "\t" not in line:
                    continue
                query, surface = line.split("\t", 1)
                surface = surface.strip()
                if query == analysis.raw and surface and surface != "+?":
                    surfaces.add(surface)
        result = tuple(sorted(surfaces))
        self._cache[cache_key] = result
        return result
