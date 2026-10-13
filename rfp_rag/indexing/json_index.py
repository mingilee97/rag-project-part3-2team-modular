"""벡터와 청크를 로컬 JSON 파일에 저장한다. 별도 DB 서버는 사용하지 않는다."""
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
from rfp_rag.contracts import Chunk


def normalize(vector: list[float]) -> list[float]:
    if not vector or any(type(value) not in (int, float) or not math.isfinite(value) for value in vector):
        raise ValueError('유효하지 않은 임베딩 벡터입니다.')
    norm = math.sqrt(sum(value * value for value in vector))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError('벡터 길이가 0 또는 유효하지 않습니다.')
    return [value / norm for value in vector]


class VectorIndex:
    def __init__(self, chunks: list[Chunk], vectors: list[list[float]], model: str, embedding_state: dict | None = None):
        if not chunks or len(chunks) != len(vectors) or len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError('청크와 벡터의 개수 또는 ID가 맞지 않습니다.')
        self.chunks = chunks
        self.vectors = [normalize(vector) for vector in vectors]
        if len({len(vector) for vector in self.vectors}) != 1:
            raise ValueError('임베딩 차원이 서로 다릅니다.')
        self.model = model
        self.embedding_state = embedding_state or {}

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'schema': 1, 'model': self.model,
                              'chunks': [asdict(chunk) for chunk in self.chunks],
                              'vectors': self.vectors, 'embedding_state': self.embedding_state}, ensure_ascii=False), encoding='utf-8')
        os.replace(temporary, path)

    @classmethod
    def load(cls, path: Path, *, model: str):
        packet = json.loads(path.read_text(encoding='utf-8'))
        if packet.get('schema') != 1 or packet.get('model') != model:
            raise ValueError('색인 형식 또는 임베딩 모델이 다릅니다. --build로 다시 만드세요.')
        return cls([Chunk(**row) for row in packet['chunks']], packet['vectors'], model, packet.get('embedding_state'))
