from abc import ABC, abstractmethod
from collections import deque
from aiogram import Bot
from aiogram.types import Message
import asyncio

from src.bot.core.parse.message import MessageParser
from src.logging.logging import get_debug_logger


debug = get_debug_logger().debug


class MessageStorage(ABC):
    def __init__(self):
        self.storage

    @abstractmethod
    def add(self, message: Message | str):
        raise NotImplementedError


class RamMessageStorage(MessageStorage):
    def __init__(self):
        self.storage = {}
        self.lock = asyncio.Lock()

    async def ensure_chat(self, chat_id: int, maxlen: int = 10):
        async with self.lock:
            if chat_id not in self.storage:
                self.storage[chat_id] = deque(maxlen=maxlen)
                debug(
                    f"Initialized message storage for chat {chat_id} with maxlen {maxlen}"
                )
                return
            dq = self.storage[chat_id]
            if getattr(dq, "maxlen", None) != maxlen:
                items = list(dq)
                self.storage[chat_id] = deque(items, maxlen=maxlen)
                debug(
                    f"Updated message storage for chat {chat_id} to new maxlen {maxlen}"
                )

    async def add(self, message):
        async with self.lock:  # Блокировка состояния, чтобы избежать "гонки"
            if message.chat.id not in self.storage:
                self.storage[message.chat.id] = deque(maxlen=10)
            self.storage[message.chat.id].append(MessageParser.message_to_text(message))

    async def add_raw(self, text: str, chat_id: int, bot: Bot):
        async with self.lock:
            if chat_id not in self.storage:
                self.storage[chat_id] = deque(maxlen=10)
            bot_name = (await bot.get_my_name()).name
            self.storage[chat_id].append(f"{bot_name}: {text}")


message_storage = (
    RamMessageStorage()
)  # Создание глобального объекта, для использования в других файлах
