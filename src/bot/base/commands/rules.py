from aiogram import types
from src.database.db_req import Table
from src.bot.functions import is_admin


class ChatRulesManager:
    def __init__(self, table: Table):
        self.table = table

    async def get_rules(self, chat_id: int) -> str:
        cfg = await self.table.select_one({"id": chat_id})
        if not cfg:
            return "Правила не установлены."
        rules = cfg.get("chat_rules", "")
        if not rules:
            return "Правила не установлены."
        return f"--Правила чата--\n\n{rules}"

    async def _ensure_admin(self, message: types.Message) -> bool:
        return await is_admin(message, message.bot)

    async def add_rules(self, message: types.Message, new_rules: str) -> str:
        if not await self._ensure_admin(message):
            return "Только администраторы могут изменять правила."

        cfg = await self.table.select_one({"id": message.chat.id})
        current_rules = cfg.get("chat_rules", "") if cfg else ""
        updated_rules = current_rules + "\n" + new_rules if current_rules else new_rules

        await self.table.update({"id": message.chat.id}, {"chat_rules": updated_rules})
        return "Правила добавлены."

    async def delete_rules(self, message: types.Message) -> str:
        if not await self._ensure_admin(message):
            return "Только администраторы могут изменять правила."

        await self.table.update({"id": message.chat.id}, {"chat_rules": ""})
        return "Правила удалены."

    async def edit_rules(self, message: types.Message, new_rules: str) -> str:
        if not await self._ensure_admin(message):
            return "Только администраторы могут изменять правила."

        await self.table.update({"id": message.chat.id}, {"chat_rules": new_rules})
        return "Правила изменены."
