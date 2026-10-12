"""공정 연결을 구현할 자리. 현재는 답변을 생성하지 않는다."""
from rfp_rag.contracts import Answer

STAGES = {
    "ingestion": "HWP·PDF·CSV 불러오기",
    "preprocessing": "글 정리와 메타데이터 정규화",
    "chunking": "청크 생성",
    "embeddings": "임베딩 생성",
    "indexing": "색인 저장과 불러오기",
    "retrieval": "근거 검색",
    "reranking": "검색 결과 재순위",
    "routing": "질문 분류",
    "generation": "근거를 이용한 답변 생성",
    "memory": "대화 맥락 관리",
    "verification": "답변과 근거 검증",
    "evaluation": "품질과 속도 평가",
}


def status() -> dict[str, str]:
    """공정 구현 후 해당 상태와 점검을 함께 갱신한다."""
    return {name: "미구현" for name in STAGES}


def ask(question: str, config: dict) -> Answer:
    if not question.strip():
        raise ValueError("질문을 입력하세요.")
    raise NotImplementedError("RAG 공정이 비어 있습니다. 검색과 답변 생성을 구현한 뒤 연결하세요.")
