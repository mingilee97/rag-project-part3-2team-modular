# 기초 RAG 인수인계

갱신일: 2026-10-13, 한국 시간.

## 목표와 결정

사용자는 빈 공정 뼈대에서, 바꾼 모듈과 비교할 수 있는 가장 원초적인 작동 기준선을 요청했다. 기존 RAG 구현을 복사하지 않는다. 정확도 개선·비용 최적화·학습·배포·원본 데이터 업로드는 이번 범위가 아니다. 실제 연결 점검은 Haiku 4.5로 성공했다. 이후 2026-10-13 팀원은 GPT-5 mini를 사용한다고 확정했으므로 팀 기본 설정을 GPT-5 mini + text-embedding-3-small로 변경했다. Haiku + 로컬 TF-IDF는 configs/haiku.toml에 분리했다. 바탕화면 키 프로그램에 OpenAI 입력칸을 추가하고 실제 실행도 확인하도록 요청받았다.

## 완료와 확인

팀 기본은 문서 읽기 → 최소 글 정리 → 문자 800/중첩 100 청킹 → text-embedding-3-small·JSON 색인 → 코사인 Top-3 → GPT-5 mini 한 번 호출이다. 공통 자료형은 유지한다. 재순위·분류·기억·답변 내용 검증·평가·LangSmith·웹/API 화면은 미구현이다. JSON 응답과 근거 ID 형식만 확인한다. 실제 API 성공 근거는 아래 Haiku 선택 설정에만 해당한다.

합성 문서 두 개에서 `claude-haiku-4-5-20251001` 호출 1회 성공. 예산 3000만 원과 필수 기능 세 개, 근거 `office.txt:c0`을 반환했다. 공급자 응답에 입력 661·출력 84토큰이 기록됐다. 품질 평가나 원본 100문서 실행 결과는 아니다. 공급자 청구액과 현재 채팅의 정확한 입력/비용 텔레메트리는 확인할 수 없다.

오프라인 unittest 12개, compileall, git diff --check 통과. 선택 의존성 pypdf 6.20.1·olefile 0.47은 프로젝트 .venv에만 설치했다. 기본 TXT·TF-IDF·HTTP 실행은 표준 라이브러리만 사용한다.

OpenAI는 두 번 모두 첫 임베딩 요청에서 HTTP 401로 중단됐다. mini·nano 생성은 실제 호출하지 못했다. 팀 기본 설정과 configs/openai.toml은 GPT-5 mini로 준비했으나 실제 성공은 미확인이다. 유효한 OpenAI 키가 필요하다. Haiku 선택 실행에는 OpenAI 키가 필요 없다.

## 키 입력 프로그램

기존 비Git 폴더 `team-dashboard-prototype/review/20261009-version-selection/claude-validation/`의 GUI·secret_store·합성 검사를 수정했다. OpenAI 입력칸을 추가하고 이전 5항목과 새 6항목 envelope를 모두 허용한다. 기존 Anthropic·LangSmith 값과 암호화 방식·바로가기는 보존한다. 키 원문은 출력하지 않았다. GUI 실행과 합성 검사 11개 통과를 확인했다. 이 변경은 팀 PR에 포함하지 않는 로컬 프로그램 변경이다.

관리 인계와 백업 위치: `C:/Users/lacos/OneDrive/Desktop/git_hub_codex/handoffs/rag-baseline-key-entry-20261013.md`.

## 실행과 제한

```powershell
.venv/Scripts/python -m rfp_rag --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
# 실제 연결을 확인했던 Haiku 설정으로 실행할 때
.venv/Scripts/python -m rfp_rag --config configs/haiku.toml --data-dir examples/synthetic --build --ask "새봄연구소 사업의 예산과 필수 기능은 무엇인가요?" --usage
python -m unittest discover -s tests
python -m rfp_rag
python -m compileall -q rfp_rag tests
git diff --check
```

실제 문서는 각자 승인된 로컬 data/raw/ 또는 --data-dir 위치에 둔다. 원본·본문·벡터·색인·키·모델·비공개 결과는 커밋하지 않는다. 예시는 examples/synthetic/에 있다. TF-IDF는 단어 일치의 한계가 있다. OCR·HWPX·표 구조 보존·CSV 메타데이터 연결·대화 기록은 미구현이다. 실제 RFP PDF·HWP 전체 실행은 미확인이다. 문서 변경 후 --build로 색인을 갱신한다.

## Git과 다음 작업

폴더: `C:/Users/lacos/OneDrive/Desktop/git_hub_codex/rag-project-part3-2team-modular`.
원격: `https://github.com/mingilee97/rag-project-part3-2team-modular`.
기준 main: 52268ca. 작업 브랜치: feature/mingilee97/pipeline-basic.
기존 로컬 docs/reports/의 보고서·PDF는 보존하고 이번 커밋에서 제외한다. main 직접 push, 보호 규칙 우회, 담당자 지정, 다른 팀원 브랜치 변경은 하지 않는다.

최종 커밋·PR·원격 동기화는 아래 완료 기록과 git status -sb, git log -1, git rev-list --left-right --count HEAD...@{upstream}로 확인한다. 남은 운영 단계는 작성자 외 팀원의 PR 검토·승인·병합이다. 원본 평가·OpenAI 인증 해결·다른 공정 개발은 추가 작업이다.

구현 커밋 `7c6ff8e`를 원격 작업 브랜치에 push했다. [PR #2](https://github.com/mingilee97/rag-project-part3-2team-modular/pull/2)를 생성했다. 보고서에 PR 링크를 넣는 후속 문서 커밋도 같은 브랜치에 저장·push한다. main은 변경하지 않았다.

## 보고서와 작업자

최신 보고서: docs/보고서/2026-10-13_기초-RAG.html.
답변 파일: docs/보고서/2026-10-13_기초-RAG.답변.json. 마지막 답변 saved_at: 2026-10-13T13:50:29+09:00. 팀 기본 GPT-5 mini 결정과 원격 상태 확인을 반영한 뒤 feedback.py resolve로 완료를 기록한다. 답변이 있는 기존 보고서는 당시 Haiku 실행 결과로 보존한다. 자동 실행에서는 새 보고서를 만들지 않는다.
실제 소유 채팅: 01a13382-57d2-7660-8d58-7da99a991fcf. 공식 1분 heartbeat rag를 연결했다. 설정 검증과 실제 예약 실행은 구분한다. 수동 writer 가드는 종료 직전에 해제한다. 답변·상태·launcher JSON은 Git 제외다.

이번 작업은 동일 채팅에서 마무리한다. 전환은 미전달이고 수신 채팅이나 동시 작성자는 없다. 단계 상태는 Git 제외 docs/handoff/baseline-continuity.json에 있다.
