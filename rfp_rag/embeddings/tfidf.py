"""모델과 API 없이 단어 빈도로 만드는 가장 단순한 TF-IDF 벡터."""
from collections import Counter
import math
import re


def tokens(text: str) -> list[str]:
    return re.findall(r'[가-힣a-z0-9]+', text.lower())


class TfidfEmbedder:
    model = 'local-tfidf'

    def __init__(self, state: dict | None = None):
        self.state = state or {}

    def fit(self, texts: list[str]):
        sets = [set(tokens(text)) for text in texts]
        vocabulary = sorted(set().union(*sets))
        if not vocabulary:
            raise ValueError('TF-IDF를 만들 단어가 없습니다.')
        frequencies = Counter(word for words in sets for word in words)
        self.state = {'vocabulary': vocabulary,
                      'idf': [math.log((1 + len(texts)) / (1 + frequencies[word])) + 1 for word in vocabulary]}

    def embed(self, texts: list[str]) -> list[list[float]]:
        words, idf = self.state['vocabulary'], self.state['idf']
        if not words or len(words) != len(idf):
            raise ValueError('TF-IDF 색인 설정이 맞지 않습니다.')
        vectors = []
        for text in texts:
            counts = Counter(tokens(text))
            vectors.append([counts[word] * weight for word, weight in zip(words, idf)])
        return vectors
