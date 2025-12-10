from aiogram import Router
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from src.bot.ai.logic.models import DefaultModels
from src.bot.ai.logic.parse import MessageParser
from src.bot.ai.logic.handler import RamMessageProcessor
import asyncio

ai_router = Router()
message_processor = RamMessageProcessor()

@ai_router.message()
async def func_handle_request(message: Message):
    if not (
        message.reply_to_message
        and message.reply_to_message.from_user.id == message.bot.id
    ):
        return 
    msg = await message.answer("печатает...")
    parsed_messages = "; ".join(message_processor.storage.get(message.chat.id, []))
    response = await asyncio.to_thread(DefaultModels.KAWAII.make_request, parsed_messages)
    print(parsed_messages)
    await msg.delete()
    await message.reply(response)

class HistoryMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        message_processor.add(message)
        
        return await handler(message, data)