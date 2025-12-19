from aiogram.types import Message
from json import loads

from src.bot.ai.service.default_models import DefaultModels
from src.bot.moderator.commands import ModeratorComands
from src.bot.functions import is_bot_admin
from src.logging.logging import get_debug_logger

debug = get_debug_logger().debug

class ModeratorMode:
    def __init__(self):
        self.activated = False
        self.model = DefaultModels.MODERATOR

    def make_request(self, text: str, rules: str, api_key: str) -> dict:
        if not self.activated:
            return {}

        msg = f"\nПравила: \n{rules}{text}"

        request_str = self.model.make_request(msg, api_key=api_key)
        debug(request_str)
        json = loads(request_str.strip())
        debug(json)
        return json

    async def process_request(self, request_result: dict, message: Message):
        if not self.activated:
            return
        chat_id = message.chat.id
        user_id = request_result.get("user_id", None)
        debug(user_id)
        action = request_result.get("action").strip().lower()
        debug(action)

        if action in ["ban", "mute", "warn", "kick"]:
            admin = await is_bot_admin(message.chat.id, message.bot)

        debug(admin)

        match action:
            case "ban":
                if admin:
                    await ModeratorComands.ban_with_id(chat_id, user_id, message.bot)
            case "mute":
                if admin:
                    await ModeratorComands.mute_with_id(chat_id, user_id, message.bot)
            case "warn":
                if admin:
                    await ModeratorComands.warn_with_id(chat_id, user_id, message.bot)
            case "kick":
                if admin:
                    await ModeratorComands.kick_with_id(chat_id, user_id, message.bot)
            case _:
                return

    def _activate(self) -> None:
        self.activated = True

    def _deactivate(self) -> None:
        self.activated = False

    def is_active(self):
        return self.activated
