# 팀 RAG · API와 모듈을 바꿔 검증하는 기본 파이프라인

**문서를 읽고, 청크로 나누고, 검색한 근거로 답변하는 최소 RAG를 구현했다.** 팀원이 API와 모듈을 바꿔 검증하고 결과를 비교할 기본 파이프라인이다. 정확도 개선이나 비용 최적화가 이번 구현의 목적은 아니다. 2026-10-13 PR #2 수정 요청에 따라, 실제 연결을 확인한 **Haiku 4.5 + 로컬 TF-IDF**를 기본값으로 선택했다. **GPT-5 mini + text-embedding-3-small**은 `configs/openai.toml`에 별도로 유지한다. OpenAI 실제 실행은 첫 임베딩 요청의 HTTP 401로 중단돼 생성 성공은 미확인이다.

```text
TXT·MD·CSV·PDF·HWP → 최소 글 정리 → 고정 길이 청크
→ 로컬 TF-IDF 벡터·JSON 색인 → 질문과 코사인 유사도 Top-3
→ Haiku 4.5에 검색 근거 전달 → 답변·근거 ID
```

기존 RAG 코드를 복사하지 않고 빈 공정 폴더에 새로 작성했다. 공통 `Document`, `Chunk`, `SearchHit`, `Answer` 규약을 유지한다. 재순위·질문 분류·대화 기억·답변 내용 검증·품질 평가는 미구현이다. 현재 상태와 다음 작업은 [인수인계](docs/handoff.md), 공정별 파일은 [공정 기준](docs/modules.md)에 있다.

## 가장 빠르게 실행하기

팀 공통 평가 질문 300개와 사용 안내는 [평가 자료](data/datasets/README.md)에 있다.

Python 3.11 이상이 필요하다. TXT·MD·CSV 실행에는 외부 패키지가 필요 없다. PDF·HWP도 읽을 때는 선택 의존성을 설치한다.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[documents]"
```

기본 실행에는 현재 프로세스의 `ANTHROPIC_API_KEY`를 설정한다. OpenAI·LangSmith 키는 필요 없다. 별도 OpenAI 설정으로 실행할 때는 `OPENAI_API_KEY`가 필요하다. Windows에서 기존 DPAPI 저장소를 사용한다면 현재 사용자 권한으로 읽을 수 있다. 암호화 키는 다른 PC나 팀원에게 자동 공유되지 않는다. 키를 코드·Git·채팅에 넣지 않는다.

합성 문서 두 개로 기본 흐름을 실행하는 명령이다. **색인 생성과 질문 벡터화는 로컬 TF-IDF로 처리하고, 근거가 있으면 답변 생성에서 Anthropic API를 호출한다.** API 사용량이 발생하므로 유효한 Anthropic 키가 필요하다.

```powershell
.venv/Scripts/python -m rfp_rag --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
```

처음 색인을 만든 뒤에는 질문만 실행한다. 문서를 바꾸면 `--build`를 다시 실행한다. 색인의 자동 갱신은 구현하지 않았다.

```powershell
.venv/Scripts/python -m rfp_rag --ask "새봄연구소 사업의 예산은 얼마인가요?"
```

실제 문서는 로컬 `data/raw/`에 넣거나 `--data-dir`/`RFP_DATA_DIR`로 위치를 지정한다. 이 저장소에는 원본 문서가 없다. 색인 파일에는 본문과 벡터가 있으므로 Git에서 제외한다. 입력 자료와 생성 답변을 자동으로 원격 저장소에 올리지 않는다.

## 설정별 실행과 차이

| 항목 | 기본값·Haiku 설정 | 별도 OpenAI 설정 |
|---|---|---|
| 설정 파일 | `configs/baseline.toml` 또는 `configs/haiku.toml` | `configs/openai.toml` |
| 답변 생성 | `claude-haiku-4-5-20251001` | `gpt-5-mini` |
| 문서·질문 벡터화 | 로컬 `local-tfidf`: 단어 빈도와 문서 빈도로 계산 | `text-embedding-3-small`: OpenAI 임베딩 API로 계산 |
| API 호출 단계 | 근거가 있는 답변 생성 | 색인 생성·질문 벡터화·근거가 있는 답변 생성 |
| 필요한 키 | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` |
| 색인 경로 | `data/index/haiku.json` | `data/index/openai.json` |
| 실제 연결 기록 | 합성 문서 두 개로 Haiku 답변 성공 | 첫 임베딩 요청 HTTP 401, GPT-5 mini 생성 미확인 |

기본 실행에는 `--config`가 필요 없다. 명시적으로 Haiku를 선택하면 같은 설정과 색인을 사용한다.

```powershell
.venv/Scripts/python -m rfp_rag --config configs/haiku.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
```

GPT-5 mini로 바꿔 검증하려면 별도 OpenAI 설정을 지정한다. 이 명령은 유료 OpenAI 임베딩과 생성 API를 사용한다. 유효한 OpenAI 키가 필요하며 실제 전체 실행 성공은 아직 확인하지 않았다.

```powershell
.venv/Scripts/python -m rfp_rag --config configs/openai.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
```

TF-IDF는 의미를 학습한 임베딩이 아니라 단어 빈도 벡터다. 동의어와 한국어 조사 처리에는 한계가 있다. 질문 벡터가 0이거나 양의 유사도를 가진 근거가 없으면 답변 생성 API를 호출하지 않고 근거 없음으로 반환한다. OpenAI 임베딩은 문서·질문을 API로 보내 벡터화하므로 TF-IDF와 처리 방식 및 API 사용 범위가 다르다. 이 저장소에서 두 방식의 정확도 우열은 평가하지 않았다.

두 방식 모두 코사인 유사도 Top-3 검색을 사용하지만 벡터 공간과 색인이 다르므로 색인을 공유하지 않는다. 이전 OpenAI 기본값의 `data/index/baseline.json`은 새 기본값에서 읽지 않는다. 설정이나 문서를 바꾸면 해당 설정으로 `--build`를 실행한다. 문서 본문과 벡터가 포함된 색인은 로컬에 보관한다.

## 제한과 확인된 실행

두 설정은 문자 기준 크기 800·중첩 100, Top-3, 출력 토큰 상한 2048을 사용한다. 별도 벡터 DB 서버, 학습, 의미 청킹, 메타데이터 필터, 재순위, 자동 재시도, 대화 기록, LangSmith, 웹 화면은 추가하지 않았다. JSON 응답과 근거 ID 형식은 확인하지만 답변 내용의 정확성을 보장하거나 별도 검증 모델을 호출하지 않는다.

TXT·MD는 UTF-8, CSV는 행을 글로 읽는다. `data_list.csv`와 문서의 메타데이터 자동 연결은 미구현이다. PDF는 텍스트 추출만 지원하며 스캔 PDF의 OCR은 미구현이다. HWP는 일반 HWP 5 본문을 읽으며 암호화·배포용 HWP, HWPX, 표 구조 보존은 지원하지 않는다. 실제 RFP PDF·HWP 전체 실행은 아직 확인하지 않았다.

2026-10-13 기존 실행에서는 합성 문서 두 개를 로컬에서 색인·검색하고 Haiku 4.5의 실제 답변을 받았다. 예산 3000만 원과 회의실 예약·예약 취소·사용 현황 조회를 답했으며 근거는 `office.txt:c0`이었다. [Haiku 보고서](docs/보고서/2026-10-13_기초-RAG.html)는 그 당시의 실행 기록이다. 이번 수정에서는 유료 API를 재호출하지 않았다. 이 기록은 연결 점검이며 정확도 평가나 원본 100문서 검증이 아니다. OpenAI는 당시 첫 임베딩 요청에서 HTTP 401로 중단돼 GPT-5 mini 생성에 도달하지 못했다. API 오류에는 키나 공급자 오류 본문을 출력하지 않는다.

## 오프라인 검사와 팀 작업

다음 검사는 API 키·모델 다운로드·유료 호출 없이 실행한다. 대역 API로 Haiku 기본 흐름과 별도 OpenAI 흐름을 점검하며 실제 공급자 성공과 구분한다.

```powershell
python -m unittest discover -s tests
python -m rfp_rag
python -m compileall -q rfp_rag tests
git diff --check
```

팀원은 최신 main에서 자기 작업 브랜치를 만들고 공정을 수정한 뒤 PR로 합친다. [팀 작업 안내](CONTRIBUTING.md)를 따른다. main에는 직접 push하지 않는다. 기본 입력·출력을 유지한 채 담당 모듈부터 교체하면 된다. API를 바꿀 때는 별도 설정과 색인으로 검증하고 결과를 기록한다. 원본 RFP·본문·색인·키·비공개 평가 결과는 커밋하지 않는다. 질문 파일 입력과 문항별 결과 저장은 미구현이며 별도 PR의 후속 작업이다.
