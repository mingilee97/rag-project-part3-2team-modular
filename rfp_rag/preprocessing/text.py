"""본문의 줄바꿈과 NUL 문자만 정리한다."""
from dataclasses import replace
from rfp_rag.contracts import Document


def clean(document: Document) -> Document:
    return replace(document, text=document.text.replace('\r\n', '\n').replace('\x00', '').strip())
