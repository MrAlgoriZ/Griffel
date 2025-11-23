from aiogram import Router, types, Bot, F
from src.bot.ai.logic.parse import get_last_messages
from src.bot.ai.logic.requests import get_response

ai_router = Router()

@ai_router.message(F.text.lower().startwith("!"))
async def handle_exclamation(message: types.Message):
    msg = await message.answer("печатает...")
    response = await get_response(message.text)
    await msg.delete()
    await message.reply(response)