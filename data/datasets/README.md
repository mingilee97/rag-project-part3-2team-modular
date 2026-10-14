# 팀 공통 평가 자료 v1.0

팀원이 RAG 시스템과 공정 모듈을 같은 질문으로 검증하고 비교하기 위한 고정 자료다. RFP 문서 100개에서 문서당 3문항을 구성해 총 300문항을 제공한다.

| 파일 | 형식 | 질문 수 | 용도 |
|---|---|---:|---|
| [dev_benchmark_v1.0.json](dev_benchmark_v1.0.json) | UTF-8 JSON (`metadata`, `items`) | 300 | 평가 정본: 질문, 기준 정답, 핵심 사실, 원문 근거 |
| [evaluation_questions.txt](evaluation_questions.txt) | UTF-8 TXT | 300 | 같은 질문을 빠르게 확인하는 열람용 자료 |
| [EVALUATION_DATASET_GUIDE.pdf](EVALUATION_DATASET_GUIDE.pdf) | PDF, 5쪽 | 별도 문항 없음 | 자료 구성과 평가 시 주의사항 |

`direct_fact`, `numeric_condition`, `multi_section`이 각각 100문항씩 있다. JSON과 TXT의 질문 ID 300개와 질문 본문이 일치한다. 두 파일이 충돌하면 JSON을 기준으로 한다. 세 파일은 제공된 원본 바이트 그대로 보관한다.

개발 중에는 필요한 문항을 선택하고, 실험을 비교할 때는 동일한 문항과 조건을 사용한다. 질문 입력에는 `question`을 사용하고, `reference_answer`, `atomic_facts`, `evidence`는 결과 채점에 사용한다. 정답과 원문 근거를 답변 생성 입력이나 검색용 문서로 넣으면 평가 결과가 왜곡될 수 있다.

v1.0은 고정된 자료다. 질문·정답·핵심 사실·근거를 임의로 수정하거나 문항을 추가하지 않는다. 오류는 팀 평가 담당자와 공유하고, 수정이 필요하면 별도 버전으로 관리한다. `reference_context_ids`는 현재 비어 있고 일부 `evidence.page`는 `null`이다.

현재 저장소에는 질문 파일을 일괄 실행하거나 자동 채점하는 기능이 없다. 이 폴더는 자료 공유 용도이며 원본 RFP 전체, 실행 결과, 키, 색인, 모델은 포함하지 않는다. JSON에는 RFP 원문 근거 발췌가 포함되어 있으므로 공개 저장소의 모든 방문자가 열람할 수 있다.
