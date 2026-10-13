# 팀 RAG · 가장 기초적인 기준선

**문서를 읽고, 청크로 나누고, 검색한 근거로 답변하는 최소 RAG를 구현했다.** 2026-10-13 사용자의 최종 선택에 따라 기본 생성 모델은 **Claude Haiku 4.5**다. OpenAI 키 인증이 실패하여 기본 검색은 API가 필요 없는 **로컬 TF-IDF + 코사인 유사도 Top-3**로 구성했다. 정확도 개선이나 비용 최적화가 목적이 아니라, 앞으로 바꾼 모듈과 비교할 수 있는 작동 기준선이 목적이다.

```text
TXT·MD·CSV·PDF·HWP → 최소 글 정리 → 고정 길이 청크
→ 로컬 TF-IDF 벡터·JSON 색인 → 질문과 코사인 유사도 Top-3
→ Haiku 4.5에 검색 근거 전달 → 답변·근거 ID
```

기존 RAG 코드를 복사하지 않고 빈 공정 폴더에 새로 작성했다. 공통 `Document`, `Chunk`, `SearchHit`, `Answer` 규약을 유지한다. 재순위·질문 분류·대화 기억·답변 검증·품질 평가는 미구현이다. 현재 상태와 다음 작업은 [인수인계](docs/handoff.md), 공정별 파일은 [공정 기준](docs/modules.md)에 있다.

## 가장 빠르게 실행하기

Python 3.11 이상이 필요하다. TXT·MD·CSV 실행에는 외부 패키지가 필요 없다. PDF·HWP도 읽을 때는 선택 의존성을 설치한다.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[documents]"
```

이 PC에서는 바탕화면 **RAG API 키 설정**을 열고 **Anthropic API 키**를 직접 입력한 뒤 **암호화 저장**을 누른다. 기존 DPAPI 저장소에서 현재 Windows 사용자 권한으로 읽는다. 기존 저장 값을 화면에 표시하거나 키 파일을 저장소에 복사하지 않는다. OpenAI 입력칸도 추가했지만 기본 Haiku 실행에는 필요 없다. LangSmith는 사용하지 않는다.

다른 PC 또는 Linux에서는 현재 프로세스의 `ANTHROPIC_API_KEY`를 직접 설정한다. Windows 암호화 키는 다른 PC나 팀원에게 자동으로 공유되지 않는다. 키를 코드·Git·채팅에 넣지 않는다.

합성 문서 두 개로 실제 모델을 호출하는 명령이다. **색인은 로컬에서 만들고, 질문 실행은 Anthropic 유료 API를 호출한다.**

```powershell
.venv/Scripts/python -m rfp_rag --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
```

처음 색인을 만든 뒤에는 질문만 실행한다. 문서를 바꾸면 `--build`를 다시 실행한다. 색인의 자동 갱신은 구현하지 않았다.

```powershell
.venv/Scripts/python -m rfp_rag --ask "새봄연구소 사업의 예산은 얼마인가요?"
```

실제 문서는 로컬 `data/raw/`에 넣거나 `--data-dir`/`RFP_DATA_DIR`로 위치를 지정한다. 이 저장소에는 원본 문서가 없다. 인덱스 파일에는 본문과 벡터가 있으므로 Git에서 제외한다. 입력 자료와 생성 답변을 자동으로 원격 저장소에 올리지 않는다.

## 설정과 제한

`configs/baseline.toml`은 Haiku 4.5, 로컬 TF-IDF, 문자 기준 크기 800·중첩 100, Top-3, 출력 토큰 상한 2048을 사용한다. 별도 벡터 DB 서버, 학습, 의미 청킹, 메타데이터 필터, 재순위, 자동 재시도, 대화 기록, LangSmith, 웹 화면은 추가하지 않았다.

TF-IDF는 단어가 겹치는 정도로 검색한다. 동의어와 한국어 조사 처리에는 한계가 있다. 질문과 겹치는 단어가 없으면 모델 호출 없이 근거 없음으로 반환한다. JSON 응답과 근거 ID 형식은 확인하지만, 답변 내용의 정확성을 보장하거나 별도 검증 모델을 호출하지 않는다.

TXT·MD는 UTF-8, CSV는 행을 글로 읽는다. `data_list.csv`와 문서의 메타데이터 자동 연결은 미구현이다. PDF는 텍스트 추출만 지원하며 스캔 PDF의 OCR은 미구현이다. HWP는 일반 HWP 5 본문을 읽으며 암호화·배포용 HWP, HWPX, 표 구조 보존은 지원하지 않는다. 실제 RFP PDF·HWP 전체 실행은 아직 확인하지 않았다.

## OpenAI로 실행하기

사용자는 처음 GPT-5 mini를 요청한 뒤 nano로 변경했다. `configs/openai.toml`에는 `text-embedding-3-small → 코사인 Top-3 → gpt-5-nano`를 남겼다. mini를 사용할 때는 그 파일의 `generation`을 `gpt-5-mini`로 바꾼다. Windows의 OpenAI 입력칸 또는 현재 프로세스의 `OPENAI_API_KEY`를 사용한다. Haiku 색인과 경로를 분리했다.

```powershell
.venv/Scripts/python -m rfp_rag --config configs/openai.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산은 얼마인가요?" --usage
```

OpenAI 실행은 2026-10-13 첫 임베딩 요청에서 HTTP 401로 중단됐다. nano·mini 생성까지 도달하지 않았으므로 실제 동작 확인이 끝난 것은 아니다. 유효한 OpenAI 키가 필요하다. API 오류에는 키나 공급자 오류 본문을 출력하지 않는다.

## 확인된 실행과 팀 작업

2026-10-13 합성 문서 두 개를 로컬에서 색인·검색하고 Haiku 4.5의 실제 답변을 받았다. 예산 3000만 원과 회의실 예약·예약 취소·사용 현황 조회를 답했으며 근거는 `office.txt:c0`이었다. 이는 연결 점검이며 정확도 평가나 원본 100문서 검증은 아니다.

오프라인 검사는 API 키·모델 다운로드·유료 호출 없이 실행한다.

```powershell
python -m unittest discover -s tests
python -m rfp_rag
python -m compileall -q rfp_rag tests
git diff --check
```

팀원은 최신 main에서 자기 작업 브랜치를 만들고 공정을 수정한 뒤 PR로 합친다. [팀 작업 안내](CONTRIBUTING.md)를 따른다. main에는 직접 push하지 않는다. 기본 입력·출력을 유지한 채 담당 모듈부터 교체하면 된다. 원본 RFP·본문·색인·키·비공개 평가 결과는 커밋하지 않는다.
