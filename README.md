# 팀 RAG · 최소 코드 뼈대

**실제 RAG 공정은 모두 미구현이다.** 기존 메인 RAG 코드를 복사하지 않고, 팀원이 각 공정을 나눠 개발할 수 있도록 폴더·공통 자료형·설정·실행 진입점만 만들었다. 외부 패키지나 모델 없이 Python 3.11 이상에서 상태를 확인할 수 있다.

사용자가 제공한 프로젝트 가이드의 열린 내용과 링크에서 별도의 베이스라인 코드를 찾지 못했다. 이 코드는 제공된 베이스라인의 복제본이 아니라, 2026-10-12 사용자 요청에 따라 새로 작성한 빈 구현 뼈대다. 현재 상태와 다음 작업은 [인수인계](docs/handoff.md)에 있다.

## 시작

```sh
git clone https://github.com/mingilee97/rag-project-part3-2team-modular.git
cd rag-project-part3-2team-modular
python -m rfp_rag
python -m unittest discover -s tests
```

`python -m rfp_rag`는 각 공정의 미구현 상태를 출력한다. `python -m rfp_rag --ask "질문"`은 미구현 안내와 종료 코드 2를 반환한다. 데이터·모델·색인을 만들거나 API를 호출하지 않는다.

## 역할별 구조

| 위치 | 구현할 역할 | 현재 상태 |
|---|---|---|
| `rfp_rag/ingestion/` | HWP·PDF·CSV 입력 | 빈 폴더 |
| `rfp_rag/preprocessing/` | 글 정리·메타데이터 정규화 | 빈 폴더 |
| `rfp_rag/chunking/` | 청크 생성 | 빈 폴더 |
| `rfp_rag/embeddings/` | 청크·질문 임베딩 | 빈 폴더 |
| `rfp_rag/indexing/` | 색인 생성·저장·불러오기 | 빈 폴더 |
| `rfp_rag/retrieval/` | 근거 검색 | 빈 폴더 |
| `rfp_rag/reranking/` | 검색 결과 재순위 | 빈 폴더 |
| `rfp_rag/routing/` | 질문 종류 분류 | 빈 폴더 |
| `rfp_rag/generation/` | 근거 기반 답변 생성 | 빈 폴더 |
| `rfp_rag/memory/` | 대화 맥락 관리 | 빈 폴더 |
| `rfp_rag/verification/` | 답변·근거 검증 | 빈 폴더 |
| `rfp_rag/evaluation/` | 정확성·근거·속도 평가 | 빈 폴더 |
| `rfp_rag/providers/` | 로컬 모델·API 연결 | 빈 폴더 |
| `rfp_rag/contracts.py` | Document·Chunk·SearchHit·Answer, 검색·생성 호출 규약 | 자료형만 구현 |
| `rfp_rag/pipeline.py` | 공정 연결 | 상태 출력과 미구현 오류만 구현 |
| `rfp_rag/settings.py`, `configs/` | 설정 읽기·실험 설정 | 최소 설정만 구현 |
| `prompts/` | 생성·분류·평가 프롬프트 | 빈 폴더 |
| `apps/api/`, `apps/web/` | API·웹 화면 | 빈 폴더 |
| `data/`, `models/`, `results/` | 로컬 입력·중간 산출물·모델·결과 | 빈 폴더, 내용은 Git 제외 |
| `notebooks/`, `deployment/` | 실험 노트북·배포 설정 | 빈 폴더 |
| `docs/reports/`, `docs/presentation/` | 보고서·발표 자료 | 빈 폴더 |
| `tests/`, `.github/` | 오프라인 점검·PR 양식·CI | 기본 점검 구성 |

Git은 빈 폴더를 저장하지 않으므로 `.gitkeep`만 넣었다. 담당 공정을 구현할 때 파일을 추가하고 해당 상태·문서·점검을 갱신한다. 재순위·질문 분류 등 선택 공정을 모두 구현해야 최소 RAG가 실행되는 것은 아니다. 우선 입력 → 청킹 → 임베딩·색인 → 검색 → 생성 흐름을 연결한다.

## 공동 작업

초대를 수락한 팀원은 저장소를 clone한 뒤 **자기 작업 브랜치 → PR → 점검·동료 승인 → main** 순서로 작업한다. [팀 작업 안내](CONTRIBUTING.md)에 GitHub 화면과 터미널 절차, 충돌 해결, 작업 재시작 방법을 정리했다. [공정별 개발 기준](docs/modules.md)에서 수정할 폴더와 입력·출력을 확인한다.

```sh
git switch main
git pull --ff-only
git switch -c feature/GITHUB_ID/chunking-fixed
# 해당 공정을 구현하고 점검한다.
python -m unittest discover -s tests
git diff --check
git add rfp_rag/chunking tests
git commit -m "Implement chunking stage"
git push -u origin feature/GITHUB_ID/chunking-fixed
```

`GITHUB_ID`는 본인의 GitHub 계정명으로 바꾼다. GitHub에서 `main` 대상으로 Pull Request를 열고 다른 팀원이 검토한다. 공정 담당자는 팀에서 정한다. `main` 보호 규칙은 자동 점검 `offline` 통과, 동료 승인 1명, 검토 대화 해결을 요구하며 강제 push와 브랜치 삭제를 막는다. 관리자도 같은 규칙을 따른다. 처음부터 영구 공정 브랜치를 병렬 유지하지 않고, 작업마다 최신 `main`에서 브랜치를 만든다.

팀원별 시작 브랜치 `work/<계정명>/starter`도 제공한다. 첫 작업에 사용할 수 있지만 기능을 미리 배정한 것은 아니다. 다음 작업부터는 위 명령으로 새 브랜치를 만든다. 저장소 설정·준비된 브랜치·확인 결과는 [브랜치 설정 기록](docs/branch-workflow-status.md)에 있다.

공정 간 입력·출력은 `contracts.py`를 기준으로 맞춘다. 모델명·검색 옵션은 구현 단계에서 `configs/`에 추가한다. 설치할 의존성은 `pyproject.toml`에 기록한다. 로컬 데이터 위치는 `RFP_DATA_DIR` 환경 변수로 바꿀 수 있다. 원본 RFP·추출 본문·실제 질문과 답변·키·모델은 커밋하지 않는다. 점검에는 합성 자료를 사용한다.
