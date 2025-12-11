from abc import ABC, abstractmethod
from collections import deque
from aiogram import Bot
from aiogram.types import Message
import asyncio

from src.bot.ai.utils.msg_parse import MessageParser

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

    async def add(self, message):
        async with self.lock: # Блокировка состояния, чтобы избежать "гонки"
            if message.chat.id not in self.storage:
                self.storage[message.chat.id] = deque(maxlen=10) # TODO добавить кастомный maxlen
            self.storage[message.chat.id].append(MessageParser.parse(message))

    async def add_raw(self, text: str, chat_id: int, bot: Bot):
        async with self.lock:
            if chat_id not in self.storage:
                self.storage[chat_id] = deque(maxlen=10)
            bot_name = await bot.get_my_name()
            self.storage[chat_id].append(f"{bot_name}: {text};")

message_storage = RamMessageStorage() # Создание глобального объекта, для использования в других файлах

# TODO добавить хранилище с помощью postgresql