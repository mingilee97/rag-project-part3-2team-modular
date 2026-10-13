"""기초 RAG의 색인 생성과 질문 실행 진입점."""
import argparse
import json
from pathlib import Path
from rfp_rag.pipeline import STAGES, ask, build, create_client, status
from rfp_rag.providers.openai_api import ProviderError
from rfp_rag.settings import load


def main() -> int:
    parser = argparse.ArgumentParser(description="팀 RAG 기초 기준선")
    parser.add_argument("--config", help="TOML 설정 파일 경로")
    parser.add_argument("--data-dir", type=Path, help="로컬 문서 폴더")
    parser.add_argument("--index", type=Path, help="로컬 JSON 색인 경로")
    parser.add_argument("--build", action="store_true", help="문서를 읽고 설정된 방식으로 색인을 만든다.")
    parser.add_argument("--ask", help="벡터 검색 후 설정된 공급자 모델에 질문한다.")
    parser.add_argument("--usage", action="store_true", help="공급자가 반환한 토큰 사용량을 표시한다.")
    args = parser.parse_args()
    try:
        config = load(args.config)
        if args.data_dir is not None:
            config['paths']['data_dir'] = args.data_dir.resolve()
        if args.index is not None:
            config['paths']['index_path'] = args.index.resolve()
        if args.ask is not None and not args.ask.strip():
            raise ValueError('질문을 입력하세요.')
        needs_api = config['models']['embedding'] != 'local-tfidf' and (args.build or args.ask is not None)
        client = create_client(config) if needs_api else None
        if args.build:
            index = build(config, client=client)
            print(f'색인 저장 완료: {len(index.chunks)}개 청크 / {config["paths"]["index_path"]}')
        if args.ask is not None:
            # 답변 생성에 쓸 클라이언트의 사용량을 같은 실행에서 기록한다.
            client = client if client is not None else create_client(config)
            answer = ask(args.ask, config, client=client)
            print(answer.text)
            print('근거: ' + (', '.join(answer.evidence_ids) or '없음'))
        elif not args.build:
            print(f"프로젝트: {config['project']['name']}")
            for name, state in status().items():
                print(f"{name}: {STAGES[name]} / {state}")
        if args.usage and client is not None:
            print(json.dumps({'api_usage': client.usage}, ensure_ascii=False))
        return 0
    except (ProviderError, ValueError, OSError, KeyError) as error:
        parser.exit(2, f"실행할 수 없습니다: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
