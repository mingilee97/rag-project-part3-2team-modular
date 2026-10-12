"""공정 사이에서 전달할 공통 자료형과 호출 규약."""
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Answer:
    text: str
    found: bool
    evidence_ids: tuple[str, ...] = ()


class Retriever(Protocol):
    def search(self, question: str, *, k: int) -> list[SearchHit]: ...


class Generator(Protocol):
    def generate(self, question: str, evidence: list[SearchHit]) -> Answer: ...
