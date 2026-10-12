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
    return config
