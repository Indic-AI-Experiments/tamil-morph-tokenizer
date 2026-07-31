from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .fst import PACKAGE_DIR


DEFAULT_VOCABULARY_DIR = PACKAGE_DIR / "data" / "vocabulary"


class FixedVocabulary:
    """Immutable line-number token IDs plus their build manifest."""

    def __init__(
        self,
        vocabulary_dir: str | Path = DEFAULT_VOCABULARY_DIR,
        *,
        allow_provisional: bool = False,
    ) -> None:
        self.vocabulary_dir = Path(vocabulary_dir)
        token_path = self.vocabulary_dir / "tokens.txt"
        manifest_path = self.vocabulary_dir / "manifest.json"
        self.tokens = tuple(token_path.read_text(encoding="utf-8").splitlines())
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self._token_to_id = {token: index for index, token in enumerate(self.tokens)}
        if len(self._token_to_id) != len(self.tokens):
            raise ValueError("Vocabulary contains duplicate token strings")
        digest = hashlib.sha256(token_path.read_bytes()).hexdigest()
        if digest != self.manifest.get("vocabulary_sha256"):
            raise ValueError("Vocabulary checksum does not match manifest")
        if len(self.tokens) != self.manifest.get("counts", {}).get("tokens"):
            raise ValueError("Vocabulary token count does not match manifest")
        tamil_grapheme_artifact = self.manifest.get("tamil_graphemes")
        if tamil_grapheme_artifact:
            grapheme_path = self.vocabulary_dir / tamil_grapheme_artifact["path"]
            grapheme_digest = hashlib.sha256(grapheme_path.read_bytes()).hexdigest()
            if grapheme_digest != tamil_grapheme_artifact["sha256"]:
                raise ValueError("Tamil grapheme alphabet checksum does not match")
        entity_artifact = self.manifest.get("entity_gazetteer")
        if entity_artifact:
            from .entity import DEFAULT_ENTITY_GAZETTEER_PATH

            entity_digest = hashlib.sha256(DEFAULT_ENTITY_GAZETTEER_PATH.read_bytes()).hexdigest()
            if entity_digest != entity_artifact.get("sha256"):
                raise ValueError("Vocabulary entity gazetteer checksum does not match")
            entity_manifest_path = DEFAULT_ENTITY_GAZETTEER_PATH.with_suffix(".manifest.json")
            entity_manifest_digest = hashlib.sha256(entity_manifest_path.read_bytes()).hexdigest()
            if entity_manifest_digest != entity_artifact.get("manifest_sha256"):
                raise ValueError("Vocabulary entity manifest checksum does not match")
        if not self.release_ready and not allow_provisional:
            raise ValueError(
                "Vocabulary is provisional; pass allow_provisional=True only for audits"
            )

    @property
    def release_ready(self) -> bool:
        return bool(self.manifest.get("release_ready"))

    def token_id(self, token: str) -> int:
        try:
            return self._token_to_id[token]
        except KeyError as exc:
            raise ValueError(f"Token is absent from the fixed vocabulary: {token}") from exc

    def __contains__(self, token: str) -> bool:
        return token in self._token_to_id

    def encode(self, tokens: tuple[str, ...] | list[str]) -> tuple[int, ...]:
        return tuple(self.token_id(token) for token in tokens)

    def decode(self, token_ids: tuple[int, ...] | list[int]) -> tuple[str, ...]:
        decoded: list[str] = []
        for token_id in token_ids:
            if not 0 <= token_id < len(self.tokens):
                raise ValueError(f"Token ID is outside the vocabulary: {token_id}")
            decoded.append(self.tokens[token_id])
        return tuple(decoded)
