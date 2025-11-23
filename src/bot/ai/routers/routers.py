from aiogram import Router, types
from src.bot.ai.logic.models import DefaultModels
from src.bot.ai.logic.parse import parse_msg
import asyncio

ai_router = Router()

@ai_router.message()
async def func_handle_request(message: types.Message):
    if not (
        message.reply_to_message
        and message.reply_to_message.from_user.id == message.bot.id
    ):
        return 
    msg = await message.answer("печатает...")
    parsed_msg = parse_msg(message)
    response = await asyncio.to_thread(DefaultModels.PETER.make_request, parsed_msg)
    await msg.delete()
    await message.reply(response)