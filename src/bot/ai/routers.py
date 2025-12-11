from aiogram import Router
from aiogram.types import Message
from aiogram import Bot
from src.bot.ai.service.default_models import DefaultModels
from src.bot.core.storage.storage import message_storage
import asyncio

ai_router = Router()

@ai_router.message()
async def func_handle_request(message: Message, bot: Bot):
    if not (
        message.reply_to_message
        and message.reply_to_message.from_user.id == message.bot.id
    ):
        return 
    msg = await message.answer("печатает...")
    await asyncio.sleep(2)
    parsed_messages = "; ".join(message_storage.storage.get(message.chat.id, []))
    response = await asyncio.to_thread(DefaultModels.KAWAII.make_request, parsed_messages)
    await msg.delete()
    await message_storage.add_raw(response, message.chat.id, bot)
    await message.reply(response)