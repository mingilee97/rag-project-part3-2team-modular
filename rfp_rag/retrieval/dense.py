"""모든 청크와 질문의 코사인 유사도를 비교해 Top-k만 반환한다."""
from rfp_rag.contracts import SearchHit
from rfp_rag.indexing.json_index import normalize


class DenseRetriever:
    def __init__(self, index, embedder):
        self.index, self.embedder = index, embedder

    def search(self, question: str, *, k: int) -> list[SearchHit]:
        if not question.strip() or type(k) is not int or k < 1:
            raise ValueError('질문과 양의 정수 k가 필요합니다.')
        raw = self.embedder.embed([question])[0]
        if raw and all(value == 0 for value in raw):
            return []
        query = normalize(raw)
        if len(query) != len(self.index.vectors[0]):
            raise ValueError('질문과 문서의 임베딩 차원이 다릅니다.')
        hits = [SearchHit(chunk, sum(a * b for a, b in zip(query, vector)))
                for chunk, vector in zip(self.index.chunks, self.index.vectors)]
        return sorted((hit for hit in hits if hit.score > 0), key=lambda hit: hit.score, reverse=True)[:k]
