from __future__ import annotations

import hmac
import os
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .codec import StructuredReversibleCodec
from .tokenizer import TamilMorphTokenizer
from .vocabulary import FixedVocabulary

MAX_INPUT_LENGTH = 1_000
Mode = Literal["best", "compact_ambiguity", "all_analyses"]


class TokenizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_INPUT_LENGTH)
    mode: Mode = "compact_ambiguity"


class TokenizedRecord(BaseModel):
    surface: str
    tokens: list[str]
    fallback: str | None
    semantic_special: str | None
    special_handling: str | None
    best_analysis: str | None
    analyses: list[str]


class TokenizeResponse(BaseModel):
    mode: Mode
    tokens: list[str]
    token_ids: list[int]
    records: list[TokenizedRecord]


@lru_cache(maxsize=3)
def get_tokenizer(mode: Mode) -> TamilMorphTokenizer:
    return TamilMorphTokenizer(mode=mode)


@lru_cache(maxsize=3)
def get_codec(mode: Mode) -> StructuredReversibleCodec:
    return StructuredReversibleCodec(tokenizer=get_tokenizer(mode))


@lru_cache(maxsize=1)
def get_vocabulary() -> FixedVocabulary:
    return FixedVocabulary()


def authorize(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("TOKENIZER_API_TOKEN")
    if not expected:
        return
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API token.")


app = FastAPI(
    title="Tamil Morph Tokenizer API",
    description="Finite-state, morphology-aware Tamil tokenization.",
    version="0.1.0-rc10",
    docs_url="/docs",
    redoc_url=None,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tokenize", response_model=TokenizeResponse)
def tokenize(
    request: TokenizeRequest,
    _: Annotated[None, Depends(authorize)],
) -> TokenizeResponse:
    tokenizer = get_tokenizer(request.mode)
    records = tokenizer.tokenize(request.text)
    encoding = get_codec(request.mode).encode_records(request.text, records)
    tokens = list(encoding.tokens)
    return TokenizeResponse(
        mode=request.mode,
        tokens=tokens,
        token_ids=get_vocabulary().encode(tokens),
        records=[
            TokenizedRecord(
                surface=record.surface,
                tokens=list(record.tokens),
                fallback=record.fallback,
                semantic_special=record.semantic_special,
                special_handling=record.special_handling,
                best_analysis=record.best_analysis.raw if record.best_analysis else None,
                analyses=[analysis.raw for analysis in record.analyses],
            )
            for record in records
        ],
    )


def main() -> None:
    import uvicorn

    uvicorn.run(
        "tamil_morph_tokenizer.api:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
