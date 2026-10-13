"""문서와 질문을 같은 OpenAI 임베딩 모델로 벡터화한다."""
from rfp_rag.providers.openai_api import ProviderError


class Embedder:
    def __init__(self, client, model: str):
        self.client, self.model = client, model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for start in range(0, len(texts), 64):
            batch = texts[start:start + 64]
            result = self.client.post('embeddings', {'model': self.model, 'input': batch,
                                                     'encoding_format': 'float'})
            try:
                data = sorted(result['data'], key=lambda row: row['index'])
                if [row['index'] for row in data] != list(range(len(batch))):
                    raise ValueError('임베딩 개수 불일치')
                vectors.extend(row['embedding'] for row in data)
            except (KeyError, TypeError, ValueError):
                raise ProviderError('임베딩 응답 형식이 맞지 않습니다.') from None
        return vectors
