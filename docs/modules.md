# 공정별 개발 기준

각 공정은 자기 폴더 안에서 구현한다. 연결이 필요한 공정 담당자와 협의한다. 2026-10-13 요청에 따라 최소 연결을 구현했다. 공통 규약은 유지하며 담당자를 지정하지 않았다.

| 공정 | 현재 기초 구현 |
|---|---|
| 입력 | `ingestion/files.py`: TXT·MD·CSV, 선택 의존성으로 PDF·일반 HWP 5 |
| 전처리 | `preprocessing/text.py`: 줄바꿈·NUL만 정리 |
| 청킹 | `chunking/fixed.py`: 문자 800, 중첩 100 |
| 벡터화 | `embeddings/tfidf.py`: 기본 로컬 TF-IDF; `embeddings/openai.py`: 선택 OpenAI |
| 색인 | `indexing/json_index.py`: 청크·벡터·TF-IDF 설정을 로컬 JSON으로 저장 |
| 검색 | `retrieval/dense.py`: 코사인 유사도 Top-3 |
| 생성 | `generation/anthropic.py`: 기본 Haiku 4.5; `generation/openai.py`: 선택 GPT-5 nano/mini |
| 공급자 연결 | `providers/`: HTTP API와 기존 Windows DPAPI 키 읽기 |
| 미구현 | 재순위·분류·기억·검증·평가, API·웹 화면 |

TF-IDF는 학습한 의미 임베딩 모델이 아니라 단어 빈도 벡터다. `decode_answer`는 JSON과 근거 ID의 형식만 확인한다. 별도의 답변 내용 검증 공정을 구현한 것은 아니다. 새 공정은 기존 기준선과 입력·출력을 비교하며 교체한다.

| 공정 | 수정 폴더 | 입력 → 출력 기준 |
|---|---|---|
| 입력 | `rfp_rag/ingestion/` | 로컬 파일 경로 → `list[Document]` |
| 전처리 | `rfp_rag/preprocessing/` | `Document` → 정리한 `Document` |
| 청킹 | `rfp_rag/chunking/` | `list[Document]` → `list[Chunk]` |
| 임베딩 | `rfp_rag/embeddings/` | 청크 또는 질문 → 벡터; 모델·차원은 설정으로 기록 |
| 색인 | `rfp_rag/indexing/` | 청크·벡터 → 색인; 검색용 불러오기 규약 제공 |
| 검색 | `rfp_rag/retrieval/` | 질문·k → `list[SearchHit]`; `Retriever.search` 규약 |
| 재순위 | `rfp_rag/reranking/` | 질문·검색 결과 → 다시 정렬한 검색 결과 |
| 질문 분류 | `rfp_rag/routing/` | 질문 → 분류 결과; 자료형은 첫 구현 때 합의 |
| 생성 | `rfp_rag/generation/` | 질문·검색 결과 → `Answer`; `Generator.generate` 규약 |
| 대화 기억 | `rfp_rag/memory/` | 대화 기록·질문 → 맥락; 세션 단위 격리 |
| 검증 | `rfp_rag/verification/` | `Answer`·근거 → 검증 결과; 자료형은 첫 구현 때 합의 |
| 평가 | `rfp_rag/evaluation/` | 합성 질문·예상 결과·답변 → 지표; 실제 평가 자료는 Git 제외 |
| 모델 연결 | `rfp_rag/providers/` | 설정 → 검색·생성에 필요한 모델 연결 |

`doc_id`와 `chunk_id`는 공정이 바뀌어도 근거를 추적할 수 있도록 유지한다. `Answer.evidence_ids`는 근거의 `chunk_id`를 가리킨다. 모델 고유 객체를 공정 경계에 노출해야 한다면 먼저 PR에서 대안을 논의한다.

여러 사람이 함께 사용하는 파일은 `contracts.py`, `pipeline.py`, `settings.py`, `pyproject.toml`, `configs/`다. 변경 전 Issue나 Draft PR에 목적을 기록한다. 개인 이름으로 소유권을 고정하지 않는다. 필요한 설정과 프롬프트는 각각 `configs/experiments/`, `prompts/<공정>/`에 분리한다.

새 공정의 기본 완료 조건은 자료형 준수, 합성 입력 점검, 오류 처리, 실행법, 구현 상태 갱신이다. 모델 품질 검증은 별도이며 오프라인 점검 통과만으로 성능 향상을 주장하지 않는다.
