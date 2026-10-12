# 팀 작업 안내

작업마다 최신 `main`에서 브랜치를 만든다. 한 브랜치에는 한 공정의 한 작업을 담고, PR로 합친다. 공정별 빈 폴더는 유지하며 기존 RAG 구현을 자동으로 가져오지 않는다.

## 처음 시작하기

1. GitHub 초대를 수락한다. 공개 코드 열람과 쓰기 권한은 별개다.
2. 저장소를 clone한다. GitHub Desktop에서는 `File → Clone repository → URL`에 저장소 주소를 넣는다.
3. `main`을 최신으로 받은 뒤 새 작업 브랜치를 만든다. 처음 준비된 `work/<계정명>/starter`를 사용해도 된다.
4. GitHub Issues의 공정 작업 양식으로 목표·담당자·입력/출력·완료 조건을 적는다. 담당자는 팀에서 합의한다.

```sh
git clone https://github.com/mingilee97/rag-project-part3-2team-modular.git
cd rag-project-part3-2team-modular
git switch main
git pull --ff-only
git switch -c feature/GITHUB_ID/chunking-fixed
```

브랜치 이름에서 `GITHUB_ID`를 본인 계정명으로 바꾼다. 기능은 `feature/<계정명>/<공정>-<작업>`, 수정은 `fix/<계정명>/<작업>`, 문서는 `docs/<계정명>/<작업>`을 사용한다. 팀원이 동시에 같은 브랜치에 push하지 않는다. 역할별 영구 브랜치나 별도 `develop`을 유지할 필요는 없다.

## 수정과 PR

1. [공정별 기준](docs/modules.md)에서 자기 폴더와 전달할 자료형을 확인한다.
2. 공정 코드와 합성 입력 점검을 함께 추가한다. 공통 규약을 바꾸면 영향을 받는 공정을 PR에 적는다.
3. 변경 파일을 확인하고 점검한 뒤 해당 파일만 커밋한다.
4. 브랜치를 push하고 GitHub의 `Compare & pull request`에서 대상이 `main`인지 확인한다. 작업 중이면 Draft PR을 만든다.
5. 완료하면 Ready for review로 바꾸고 작성자 외 팀원 한 명에게 검토를 요청한다. 자동 점검과 승인 1명, 검토 대화 해결을 모두 마친 뒤 Squash and merge한다.

```sh
python -m unittest discover -s tests
python -m compileall -q rfp_rag tests
git diff --check
git diff
git add rfp_rag/chunking tests
git commit -m "Implement fixed chunking"
git push -u origin feature/GITHUB_ID/chunking-fixed
```

웹에서만 수정할 때도 새 브랜치를 선택한 뒤 파일을 편집하고 PR을 연다. GitHub Desktop에서는 `Current Branch → New Branch`, 수정 후 `Commit`, `Publish branch`, `Create Pull Request` 순서를 따른다. 승인 뒤 코드를 다시 바꾸면 이전 승인이 해제되므로 다시 검토받는다.

현재 CI는 Python 표준 라이브러리만 사용한다. 공정에 외부 패키지를 추가할 때는 `pyproject.toml`과 CI 설치 절차를 같은 PR에서 함께 바꾼다. CI에는 모델 다운로드·원본 데이터·API 키·유료 호출을 넣지 않는다. 새 공정을 구현하면 `pipeline.status()`와 관련 점검도 실제 상태에 맞게 바꾼다.

## 다른 사람의 변경 받기

미커밋 파일이 있으면 먼저 본인 브랜치에 저장한다. 변경을 남긴 채 다른 브랜치로 이동하거나 강제로 초기화하지 않는다.

```sh
git fetch origin
git merge origin/main
# 충돌이 있으면 아래 절차로 해결한다.
python -m unittest discover -s tests
git diff --check
git push
```

충돌은 표시된 파일에서 양쪽 변경의 목적을 확인해 수정하고 `git add <파일>`과 `git commit`으로 해결한다. 합성 입력 점검 후 push한다. 진행을 취소하려면 `git merge --abort`를 사용한다. 공유한 브랜치에 force push하지 않는다.

## 병합 후 다음 작업

```sh
git switch main
git pull --ff-only
git switch -c feature/GITHUB_ID/retrieval-dense
```

이전 브랜치는 병합 후 GitHub가 자동으로 삭제한다. 로컬 브랜치 삭제는 완료를 확인한 사용자가 선택한다. `main`에는 직접 push하지 않는다. 보호 규칙 때문에 막히면 승인·자동 점검·대화 해결 상태를 확인한다. 관리자도 규칙을 우회하지 않는다.

담당자와 검토자가 아직 초대를 수락하지 않았다면 Draft PR을 먼저 올려 둘 수 있다. 실제 승인과 병합은 쓰기 권한이 있는 다른 팀원이 참여한 뒤 진행한다.
