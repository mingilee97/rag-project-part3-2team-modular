"""설정과 구현 상태를 확인하는 실행 진입점."""
import argparse
from rfp_rag.pipeline import STAGES, ask, status
from rfp_rag.settings import load


def main() -> int:
    parser = argparse.ArgumentParser(description="팀 RAG 코드 뼈대")
    parser.add_argument("--config", help="TOML 설정 파일 경로")
    parser.add_argument("--ask", help="질문 입력. 공정 구현 전에는 오류로 종료한다.")
    args = parser.parse_args()
    try:
        config = load(args.config)
        if args.ask is not None:
            print(ask(args.ask, config).text)
        else:
            print(f"프로젝트: {config['project']['name']}")
            for name, state in status().items():
                print(f"{name}: {STAGES[name]} / {state}")
        return 0
    except (NotImplementedError, ValueError, OSError, KeyError) as error:
        parser.exit(2, f"실행할 수 없습니다: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
