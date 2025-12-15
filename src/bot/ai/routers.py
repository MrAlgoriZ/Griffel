from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
import asyncio
import time

from src.bot.ai.service.default_models import DefaultModels, Model
from src.bot.core.parse.message import MessageParser
from src.bot.core.storage.storage import message_storage
from src.database.db_req import Table
from src.utils.env import Env
from src.logging.logging import get_debug_logger

debug = get_debug_logger().debug

last_ask_time: dict[int, float] = {}

ai_router = Router()


@ai_router.message(Command("addkey"))
async def func_add_key(message: Message, command: CommandObject):
    if not command.args:
        await message.reply("Пожалуйста, укажите ключ: /addkey <ваш_ключ>")
        return
    key = command.args.strip()
    chat_id = message.chat.id
    table = Table(Env.DATABASE.table)
    if Model.test_api_key(key):
        await table.update({"id": chat_id}, {"openrouter_key": key})
        await message.reply("Ключ OpenRouter сохранен.")
    else:
        await message.reply("Недействительный ключ OpenRouter!")


@ai_router.message(Command("ask"))
async def func_handle_request(message: Message, bot: Bot, command: CommandObject):
    chat_id = message.chat.id
    table = Table(Env.DATABASE.table)
    cfg = await table.select_one({"id": chat_id}) or {}  # Загрузка конфигурации чата

    if api_key := cfg.get("openrouter_key"):
        current_time = time.time()
        if chat_id in last_ask_time and current_time - last_ask_time[chat_id] < 5:
            await message.reply(
                "Пожалуйста, подождите 5 секунд перед следующим запросом /ask."
            )
            return
        last_ask_time[chat_id] = current_time
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
        current_parsed = MessageParser.message_to_text(message)
        if storage and storage[-1] == current_parsed:
            storage.pop()

        if getattr(command, "args", None):
            current_question = f"{message.from_user.full_name}: {command.args.strip()}"
        else:
            current_question = MessageParser.message_to_text(message)

        history_block = "\n".join(storage) if storage else ""
        parsed_messages = f"\nКонтекст: \n{history_block}\nТекущий вопрос: {current_question}\nТвой ответ:"
        debug(parsed_messages)
        try:
            response = await asyncio.to_thread(
                model_obj.make_request, parsed_messages, api_key=api_key
            )
        except Exception as e:
            debug(f"Error in AI request: {e}")
            await msg.delete()
            await message.reply(
                "Произошла ошибка, ответ не получен. Пожалуйста, попробуйте позже."
            )
            return

        await msg.delete()
        if response:
            debug("AI responsed successfully")
            await message_storage.add_raw(response, chat_id, bot)
            await message.reply(response)
            return
        await message.reply("Произошла ошибка, ответ не получен. Попробуйте позже.")
    else:
        await message.reply(
            "Ключ OpenRouter не настроен для этого чата. Пожалуйста, установите ключ с помощью команды /addkey <ваш_ключ>."
        )
