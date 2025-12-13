from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
import asyncio

from src.bot.ai.service.default_models import DefaultModels, Model
from src.bot.ai.utils.msg_parse import MessageParser
from src.bot.core.storage.storage import message_storage
from src.database.db_req import Table
from src.utils.env import Env
from src.logging.logging import get_debug_logger

debug = get_debug_logger().debug

ai_router = Router()


@ai_router.message(Command("ask"))
async def func_handle_request(message: Message, bot: Bot, command: CommandObject):
    chat_id = message.chat.id
    table = Table(Env.DATABASE.table)
    cfg = await table.select_one({"id": chat_id}) or {}  # Загрузка конфигурации чата

    bot_mode = (cfg.get("bot_mode") or "SMART").upper()  # Получение режима бота
    if bot_mode == "CUSTOM":
        custom_prompt = cfg.get("prompt") or DefaultModels.SMART.system_prompt
        model_obj = Model(
            system_prompt=custom_prompt,
        )
    else:
        model_obj = getattr(DefaultModels, bot_mode, None)
        if not model_obj:
            model_obj = DefaultModels.SMART

    msg = await message.answer("печатает...")
    storage = list(message_storage.storage.get(chat_id, []))

    if getattr(command, "args", None):
        current_question = f"{message.from_user.full_name}: {command.args.strip()}"
    else:
        current_question = MessageParser.parse(message)

    history_block = "\n".join(storage) if storage else ""
    parsed_messages = f"\nКонтекст: \n{history_block}\nТекущий вопрос: {current_question}\nТвой ответ:"
    debug(parsed_messages)
    response = await asyncio.to_thread(model_obj.make_request, parsed_messages)
    match response:
        case None | "":
            debug("AI returned empty response")
        case _:
            debug("AI responsed successfully")
    await msg.delete()
    await message_storage.add_raw(response, chat_id, bot)
    await message.reply(response)
