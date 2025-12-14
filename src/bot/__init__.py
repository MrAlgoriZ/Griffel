from aiogram import Bot
from src.utils.env import Env

from aiogram.client.default import DefaultBotProperties

bot = Bot(Env.TELEGRAM, default=DefaultBotProperties())
