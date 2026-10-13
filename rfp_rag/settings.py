"""표준 라이브러리로 설정을 읽는다. 외부 서비스에는 연결하지 않는다."""
import os
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def load(path: str | Path | None = None) -> dict:
    config_path = Path(path) if path is not None else ROOT / "configs/baseline.toml"
    with config_path.open("rb") as stream:
        config = tomllib.load(stream)
    data_dir = Path(os.environ.get("RFP_DATA_DIR") or config["paths"]["data_dir"])
    config["paths"]["data_dir"] = data_dir if data_dir.is_absolute() else ROOT / data_dir
    index_path = Path(config["paths"]["index_path"])
    config["paths"]["index_path"] = index_path if index_path.is_absolute() else ROOT / index_path
    size, overlap = config['chunking']['size'], config['chunking']['overlap']
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError('청크 크기와 중첩 설정을 확인하세요.')
    for value in (config['retrieval']['top_k'], config['generation']['max_output_tokens']):
        if type(value) is not int or value < 1:
            raise ValueError('검색 개수와 출력 토큰 한도는 양의 정수여야 합니다.')
    provider, embedding = config['models']['provider'], config['models']['embedding']
    if provider not in ('anthropic', 'openai') or (provider == 'anthropic' and embedding != 'local-tfidf'):
        raise ValueError('Anthropic은 local-tfidf, OpenAI는 local-tfidf 또는 임베딩 API를 사용하세요.')
    return config
