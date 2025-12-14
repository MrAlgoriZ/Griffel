from pathlib import Path
from dataclasses import dataclass
import json
from cachetools import cached


@cached({})
def load_config(path: Path = Path("config/phrases.json")) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@dataclass
class ConfigSystemPrompts:
    AGRESSIVE_PROMPT = load_config().get("system_prompts").get("AGRESSIVE_PROMPT")
    PETER_PROMPT = load_config().get("system_prompts").get("PETER_PROMPT")
    SMART_PROMPT = load_config().get("system_prompts").get("SMART_PROMPT")
    MODERATOR_PROMPT = load_config().get("system_prompts").get("MODERATOR_PROMPT")
    KAWAII_PROMPT = load_config().get("system_prompts").get("KAWAII_PROMPT")


@dataclass
class ConfigBasePhrases:
    START = load_config().get("base_phrases").get("start")
    HELP = load_config().get("base_phrases").get("help")
    SUPPORT = load_config().get("base_phrases").get("support")


@dataclass
class Config:
    SYSTEM_PROMPTS = ConfigSystemPrompts
    BASE_PHRASES = ConfigBasePhrases
