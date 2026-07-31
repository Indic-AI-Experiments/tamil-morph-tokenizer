from __future__ import annotations

from dataclasses import dataclass

from .analysis import MorphAnalysis
from .generation import FlookupGenerator


MAX_REALIZATION_VARIANTS = 16
REALIZATION_TOKENS = tuple(f"<REALIZATION_{index}>" for index in range(1, MAX_REALIZATION_VARIANTS))


@dataclass(frozen=True)
class RealizationDecision:
    strategy: str
    candidates: tuple[str, ...]
    selected_index: int | None
    tokens: tuple[str, ...]
    exact: bool

    @property
    def selected_surface(self) -> str | None:
        if self.selected_index is None:
            return None
        if not 0 <= self.selected_index < len(self.candidates):
            return None
        return self.candidates[self.selected_index]


class RealizationSelector:
    """Choose the minimum bounded token needed to recover an input surface."""

    def __init__(self, generator: FlookupGenerator | None = None) -> None:
        self.generator = generator or FlookupGenerator()

    def select(self, surface: str, analysis: MorphAnalysis) -> RealizationDecision:
        candidates = self.generator.generate(analysis)
        if surface not in candidates:
            return RealizationDecision(
                strategy="byte_fallback",
                candidates=candidates,
                selected_index=None,
                tokens=(),
                exact=False,
            )

        selected_index = candidates.index(surface)
        if selected_index == 0:
            return RealizationDecision(
                strategy="unique" if len(candidates) == 1 else "default",
                candidates=candidates,
                selected_index=selected_index,
                tokens=(),
                exact=True,
            )
        if selected_index < MAX_REALIZATION_VARIANTS:
            return RealizationDecision(
                strategy="variant",
                candidates=candidates,
                selected_index=selected_index,
                tokens=(f"<REALIZATION_{selected_index}>",),
                exact=True,
            )
        return RealizationDecision(
            strategy="byte_fallback",
            candidates=candidates,
            selected_index=None,
            tokens=(),
            exact=False,
        )

    @staticmethod
    def realize(decision: RealizationDecision) -> str | None:
        return decision.selected_surface if decision.exact else None
