from pathlib import Path
from dataclasses import dataclass
import json
from cachetools import cached

@cached({})
def load_config(path: Path = Path("config/config.json")) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

@dataclass
class Config:
    DEFAULT_PROMPT=load_config().get("DEFAULT_PROMPT")