# 기초 RAG 인수인계

갱신일: 2026-10-13, 한국 시간.

## 목표와 결정

팀원들이 API와 공정 모듈을 바꿔 검증하고 결과를 비교할 기본 파이프라인을 유지한다. 빈 공정 뼈대에서 최소 흐름을 구현했으며 기존 RAG 구현을 복사하지 않았다. 정확도 개선·비용 최적화·학습·배포·원본 데이터 업로드는 이번 범위가 아니다.

2026-10-13 Haiku 4.5 + 로컬 TF-IDF의 실제 연결을 확인했다. 이후 GPT-5 mini + text-embedding-3-small을 기본으로 선택했으나 OpenAI 인증 오류로 전체 실행을 검증하지 못했다. PR #2 수정 요청에 따라 유료 API를 재호출하지 않고, 검증된 Haiku 경로를 기본값으로 선택했다. GPT-5 mini 설정은 `configs/openai.toml`에 별도로 유지한다.

## 구현과 검증 범위

기본 흐름은 문서 읽기 → 최소 글 정리 → 문자 800/중첩 100 청킹 → 로컬 TF-IDF·JSON 색인 → 코사인 Top-3 → Haiku 4.5 답변이다. 공통 `Document`, `Chunk`, `SearchHit`, `Answer` 규약을 유지한다. 재순위·분류·기억·답변 내용 검증·평가·LangSmith·웹/API 화면은 미구현이다. JSON 응답과 근거 ID 형식만 확인한다.

당시 합성 문서 두 개에서 `claude-haiku-4-5-20251001` 생성 호출 1회가 성공했다. 예산 3000만 원과 필수 기능 세 개, 근거 `office.txt:c0`을 반환했다. 공급자 응답에는 입력 661·출력 84토큰이 기록됐다. 품질 평가나 원본 100문서 실행 결과는 아니다. [당시 Haiku 실행 보고서](보고서/2026-10-13_기초-RAG.html)에 결과를 보존했다. 이번 수정에서 실제 API를 재호출하지 않았다.

OpenAI는 당시 첫 임베딩 요청의 HTTP 401로 중단됐다. GPT-5 mini·nano 생성은 실제 호출하지 못했다. 별도 OpenAI 설정의 실제 성공은 미확인이며 유효한 `OPENAI_API_KEY`로 추가 검증해야 한다. 오프라인 대역 API 검사는 실제 공급자 인증이나 응답 성공의 근거가 아니다.

이번 수정 후 오프라인 unittest 13개, 구현 상태 출력, compileall, git diff --check를 통과했다. 기본값과 명시적 Haiku 설정의 일치, 별도 OpenAI 설정과 색인 분리, 합성 입력으로 두 공급자 흐름과 오류 경계를 점검했다.

## 실행과 설정 교체

Python 3.11 이상을 사용한다. 설치와 키 설정은 [README](../README.md)를 따른다. 기본 실행에는 `ANTHROPIC_API_KEY`, 별도 OpenAI 실행에는 `OPENAI_API_KEY`가 필요하다. 키를 코드·Git·채팅에 넣지 않는다.

```powershell
# 기본값: 로컬 TF-IDF로 검색하고 Haiku로 답변한다.
.venv/Scripts/python -m rfp_rag --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
# 같은 Haiku 경로를 명시적으로 선택한다.
.venv/Scripts/python -m rfp_rag --config configs/haiku.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
# 별도 OpenAI 경로: 임베딩과 GPT-5 mini 생성 API를 사용한다. 실제 성공은 미확인이다.
.venv/Scripts/python -m rfp_rag --config configs/openai.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
```

TF-IDF는 로컬에서 단어·문서 빈도로 벡터를 만든다. 동의어와 한국어 조사 처리에는 한계가 있다. OpenAI 설정은 `text-embedding-3-small` API로 문서와 질문을 벡터화한다. 두 경로 모두 코사인 Top-3를 사용하지만 검색 품질의 우열은 평가하지 않았다. Haiku 색인은 `data/index/haiku.json`, OpenAI 색인은 `data/index/openai.json`으로 분리한다. 이전 OpenAI 기본값의 `data/index/baseline.json`은 새 기본값에서 사용하지 않는다. 문서나 설정을 바꾸면 해당 설정으로 `--build`를 실행한다.

실제 문서는 승인된 로컬 `data/raw/` 또는 `--data-dir` 위치에 둔다. 합성 예시는 `examples/synthetic/`에 있다. 원본·본문·벡터·색인·키·모델·비공개 결과는 커밋하지 않는다. OCR·HWPX·표 구조 보존·CSV 메타데이터 연결·대화 기록은 미구현이다. 실제 RFP PDF·HWP 전체 실행은 미확인이다.

오프라인 검사는 API 키·다운로드·유료 호출 없이 수행한다.

```powershell
python -m unittest discover -s tests
python -m rfp_rag
python -m compileall -q rfp_rag tests
git diff --check
```

## Git과 다음 작업

저장소: [mingilee97/rag-project-part3-2team-modular](https://github.com/mingilee97/rag-project-part3-2team-modular).
작업 브랜치: `feature/mingilee97/pipeline-basic`. 대상 브랜치: `main`.
[PR #2](https://github.com/mingilee97/rag-project-part3-2team-modular/pull/2)에서 김현경 님의 수정 요청을 반영한다. 수정 전 기준 커밋은 `f63afee`, 최초 Haiku 구현 커밋은 `7c6ff8e`다. 후속 커밋과 push 상태는 PR 및 다음 명령으로 확인한다.

```sh
git status -sb
git log -1 --oneline
git rev-list --left-right --count HEAD...@{upstream}
```

다음 단계는 작성자 외 팀원의 재검토·승인·병합이다. 기존 수정 요청을 강제로 해제하거나 보호 규칙을 바꾸지 않는다. 질문 파일 입력과 문항별 결과 저장은 별도 PR로 진행할 후속 요구사항이다. OpenAI 인증 해결과 실제 실행 검증, 원본 평가, 다른 공정 개발은 추가 작업이다.
