from aiogram import Router, types
from aiogram.filters import Command
from src.utils.config import Config

base_router = Router()

@base_router.message(Command("start"))
async def func_start(message: types.Message):
    await message.reply(Config.BASE_PHRASES.START)

@base_router.message(Command("help"))
async def func_help(message: types.Message):
    await message.reply(Config.BASE_PHRASES.HELP)