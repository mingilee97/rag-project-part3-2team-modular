# 브랜치 작업 구조

2026-10-12 사용자 요청으로 팀원이 독립된 브랜치에서 공정 코드를 수정하고 PR로 합치도록 구성한다. 실제 RAG 공정은 여전히 비어 있다.

## 적용할 저장소 설정

- 기본 브랜치: `main`.
- `main`은 PR과 작성자 외 승인 1명, 자동 점검 `offline` 통과, 검토 대화 해결이 필요하다.
- 새 코드를 push하면 기존 승인을 해제한다. 병합 전 최신 `main` 반영을 요구한다.
- 관리자도 보호 규칙을 따르며 force push·브랜치 삭제를 허용하지 않는다.
- 병합 방식은 Squash만 허용한다. 병합된 작업 브랜치는 자동 삭제한다.
- 병합이 끝난 뒤 새 작업은 최신 `main`에서 만든다.

## 첫 작업용 브랜치

| 계정 | 시작 브랜치 |
|---|---|
| mingilee97 | `work/mingilee97/starter` |
| HyeongyeongKim | `work/HyeongyeongKim/starter` |
| seolwoom | `work/seolwoom/starter` |
| 1young-codes | `work/1young-codes/starter` |
| eugene527 | `work/eugene527/starter` |

모두 같은 준비 완료 `main`에서 시작한다. 공정 담당이나 수정 내용은 미리 배정하지 않는다. 초대 수락 전에는 공개 코드 열람만 가능하며, 수정 내용 push에는 쓰기 권한이 필요하다.

설정과 브랜치는 준비 PR 병합 후 적용한다. 적용한 값은 별도 로컬 작업 기록과 GitHub API로 확인한다. 이 준비 PR은 보호 규칙을 켜기 전에 자동 점검을 통과한 뒤 병합하며 동료 승인으로 간주하지 않는다.
