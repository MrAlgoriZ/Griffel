from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass

ENV = load_dotenv()

@dataclass
class Env:
    IS_LOADED: bool = ENV
    TELEGRAM = getenv("TELEGRAM_TOKEN")
    OPEN_ROUTER = getenv("OPEN_ROUTER_TOKEN")
    TELEGRAM_API = getenv("TELGRAM_API")
    TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH")