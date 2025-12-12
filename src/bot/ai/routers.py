from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from src.bot.ai.service.default_models import DefaultModels, Model
from src.bot.ai.utils.msg_parse import MessageParser
from src.bot.core.storage.storage import message_storage
from src.database.db_req import Table
from src.utils.env import Env
import asyncio

ai_router = Router()

@ai_router.message(Command("ask"))
async def func_handle_request(message: Message, bot: Bot, command: CommandObject):
    """
    Handle /ask <question> command. Prefer the command arguments from `CommandObject.args`
    as the question text; fall back to parsing the message when args are empty.
    """
    chat_id = message.chat.id
    table = Table(Env.DATABASE.table)
    cfg = await table.select_one({"id": chat_id}) or {}

    # Ensure storage deque respects chat-specific historyMaxlen
    history_len = cfg.get("history_maxlen") or 10
    await message_storage.ensure_chat(chat_id, maxlen=history_len)

    # Prepare model: if bot_mode == CUSTOM, create a dynamic Model with custom prompt
    bot_mode = (cfg.get("bot_mode") or "SMART").upper()
    if bot_mode == "CUSTOM":
        # Create a dynamic CUSTOM model with the custom prompt from database
        custom_prompt = cfg.get("prompt") or DefaultModels.SMART.system_prompt
        model_obj = Model(
            system_prompt=custom_prompt,
        )
    else:
        # Use pre-defined model or fall back to SMART
        model_obj = getattr(DefaultModels, bot_mode, None)
        if not model_obj:
            model_obj = DefaultModels.SMART

    msg = await message.answer("печатает...")
    storage = list(message_storage.storage.get(chat_id, []))
    # Prefer command arguments as the question text when present
    if getattr(command, "args", None):
        current_question = command.args.strip()
    else:
        current_question = MessageParser.parse(message)

    # Combine stored history and current question (prompt is in model.system_prompt, not here)
    history_block = "\n".join(storage) if storage else ""
    parsed_messages = (
        f"\nКонтекст: \n{history_block}\nТекущий вопрос: {current_question}\nТвой ответ:"
    )
    # Call model with only the message argument
    response = await asyncio.to_thread(model_obj.make_request, parsed_messages)
    await msg.delete()
    await message_storage.add_raw(response, chat_id, bot)
    await message.reply(response)