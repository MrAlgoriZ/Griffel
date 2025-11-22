from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass

ENV = load_dotenv()

@dataclass
class Env:
    IS_LOADED=ENV
    TELEGRAM=getenv("TELEGRAM_TOKEN")
    OPEN_ROUTER=getenv("OPEN_ROUTER_TOKEN")