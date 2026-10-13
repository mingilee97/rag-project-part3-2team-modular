"""문자 수 기준으로 겹치는 고정 길이 청크를 만든다."""
from rfp_rag.contracts import Chunk, Document


def split(documents: list[Document], *, size: int, overlap: int) -> list[Chunk]:
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError('청크 크기는 양의 정수, 중첩은 0 이상이며 크기보다 작아야 합니다.')
    chunks = []
    for document in documents:
        for start in range(0, len(document.text), size - overlap):
            text = document.text[start:start + size]
            if text.strip():
                chunks.append(Chunk(f'{document.doc_id}:c{start}', document.doc_id, text,
                                    {**document.metadata, 'start': start}))
            if start + size >= len(document.text):
                break
    return chunks
