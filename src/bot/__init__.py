from aiogram import Bot
from src.utils.env import Env

from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

bot = Bot(Env.TELEGRAM, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))