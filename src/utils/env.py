from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass

ENV = load_dotenv()


@dataclass
class DatabaseEnv:
    user = getenv("DATABASE_USER")
    password = getenv("DATABASE_USER_PASSWORD")
    database = getenv("DATABASE_NAME")
    host = getenv("DATABASE_HOST")
    table = getenv("TABLE_NAME")


@dataclass
class Env:
    IS_LOADED: bool = ENV
    TELEGRAM: str = getenv("TELEGRAM_TOKEN")
    OPEN_ROUTER: str = getenv("OPEN_ROUTER_TOKEN")
    DATABASE = DatabaseEnv
