import random
from aiogram.types import Message
from aiogram import Bot
import asyncio

from src.bot.ai.service.default_models import DefaultModels, Model
from src.bot.ai.utils.msg_parse import ResponseProcessor
from src.bot.core.storage.storage import message_storage
from src.utils.config import ConfigBasePhrases
from src.logging.logging import get_debug_logger
from src.database.db_req import Table
from src.utils.env import Env

debug = get_debug_logger().debug


class AutoAnswer:
    def __init__(self, message: Message, bot: Bot):
        self.message = message
        self.bot = bot
        self.auto_replies = [
            self.support,
            self.ai_answer,
        ]

    async def get_auto_reply(self):
        roll = random.random()

        if roll < 0.04:  # 4%
            await self.support()

        elif roll < 0.06:  # 6% (4% + 2%)
            await self.support()
            await self.ai_answer()

        else:  # 94%
            await self.ai_answer()

    async def support(self):
        await self.message.answer(ConfigBasePhrases.SUPPORT)

    async def ai_answer(self):
        chat_id = self.message.chat.id
        table = Table(Env.DATABASE.table)
        cfg = (
            await table.select_one({"id": chat_id}) or {}
        )  # Загрузка конфигурации чата

        if api_key := cfg.get("openrouter_key"):
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

            msg = await self.message.answer("печатает...")
            storage = list(message_storage.storage.get(chat_id, []))
            current_question = storage[-1]
            storage.pop()

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
                await self.message.reply(
                    "Произошла ошибка, ответ не получен. Попробуйте позже."
                )
                return

            await msg.delete()
            if response:
                debug("AI responsed successfully")
                response = ResponseProcessor.process(response)
                await message_storage.add_raw(response, chat_id, self.bot)
                await self.message.reply(ResponseProcessor)
                return
            await self.message.reply(
                "Произошла ошибка, ответ не получен. Попробуйте позже."
            )
