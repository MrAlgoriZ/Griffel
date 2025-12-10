from abc import ABC, abstractmethod
from collections import deque
from aiogram.types import Message

from src.bot.ai.logic.parse import MessageParser

class MessageProcessor(ABC):
    def __init__(self):
        self.storage
    
    @abstractmethod
    def add(self, message: Message):
        raise NotImplementedError


class RamMessageProcessor(MessageProcessor):
    def __init__(self):
        self.storage = {}

    def add(self, message):
        if message.chat.id not in self.storage:
            self.storage[message.chat.id] = deque(maxlen=10)
        self.storage[message.chat.id].append(MessageParser.parse(message))