from aiogram import Router, types, F, Bot
from aiogram.filters import Command

from src.utils.config import Config
from src.utils.env import Env
from src.bot.functions import is_admin
from src.database.db_req import Table
from src.bot.ai.service.default_models import DefaultModels
from src.bot.base import keyboards
from src.bot.core.storage.storage import message_storage

base_router = Router()

pending_actions: dict[int, dict] = {}


class PendingActionProcessor:
    def __init__(self, table: Table, cfg: dict):
        self.table = table
        self.cfg = cfg

    async def process(self, action: str, message: types.Message) -> tuple[str, bool]:
        match action:
            case "set_history":
                return await self._process_set_history(message)
            case "set_prompt":
                return await self._process_set_prompt(message)
            case "set_botname":
                return await self._process_set_botname(message)
            case "set_openrouter":
                return await self._process_set_openrouter(message)
            case _:
                return "Действие не распознано или срок действия уже истек.", False

    async def _process_set_history(self, message: types.Message) -> tuple[str, bool]:
        try:
            value = int(message.text.strip())
        except Exception:
            return (
                "❌ Пожалуйста, введите положительное целое число, и попробуйте снова.",
                True,
            )
        max_allowed = 25 if self.cfg.get("is_premium") else 10
        if value > max_allowed:
            return (
                f"❌ Значение слишком больше, максимальное: {max_allowed} сообщений. Попробуйте снова",
                True,
            )
        await self.table.update({"id": message.chat.id}, {"history_maxlen": value})
        await message_storage.ensure_chat(message.chat.id, maxlen=value)
        return f"✅ Длина контекста изменена на: {value} сообщений", False

    async def _process_set_prompt(self, message: types.Message) -> tuple[str, bool]:
        new_prompt = message.text.strip()
        if not new_prompt:
            return "❌ Промпт не может быть пустым. Попробуйте снова", True
        await self.table.update(
            {"id": message.chat.id}, {"prompt": new_prompt, "bot_mode": "CUSTOM"}
        )
        return "✅ Промпт обновлен, и режим бота изменен на 'CUSTOM'", False

    async def _process_set_botname(self, message: types.Message) -> tuple[str, bool]:
        name = message.text.strip()
        if len(name) > 15:
            return (
                "❌ Имя слишком большое, максимум 15 символов. Попробуйте снова",
                True,
            )
        await self.table.update({"id": message.chat.id}, {"bot_name": name})
        return f"✅ Имя бота изменено на '{name}'.", False

    async def _process_set_openrouter(self, message: types.Message) -> tuple[str, bool]:
        key = message.text.strip()
        if len(key) < 10:
            return (
                "❌ Предоставленный ключ выглядит слишком коротким; пожалуйста, перепроверьте и отправьте заново.",
                True,
            )
        await self.table.update({"id": message.chat.id}, {"openrouter_key": key})
        return "✅ Ключ OpenRouter сохранен.", False

@base_router.message(Command("help"))
async def func_help(message: types.Message):
    await message.reply(Config.BASE_PHRASES.HELP)


@base_router.message(Command("config"))
async def func_config(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply(
            "Только администраторы чата могут смотреть и изменять конфигурацию."
        )
        return

    table = Table(Env.DATABASE.table)
    chat_id = message.chat.id

    cfg = await table.select_one({"id": chat_id})
    default_prompt = DefaultModels.SMART.system_prompt
    if not cfg:
        cfg = await table.insert(
            {
                "id": chat_id,
                "prompt": default_prompt,
                "history_maxlen": 10,
                "is_premium": False,
                "bot_name": "",
                "bot_mode": "SMART",
                "chat_rules": "",
                "openrouter_key": "",
            }
        )

    text = keyboards.build_config_text(cfg)
    kb = keyboards.build_config_keyboard()
    await message.reply(text, reply_markup=kb)


@base_router.callback_query(F.data.startswith("cfg:"))
async def callback_config(cb: types.CallbackQuery, bot: Bot):
    data = cb.data.split(":", 2)
    action = data[1] if len(data) > 1 else ""
    param = data[2] if len(data) > 2 else None

    chat_id = cb.message.chat.id
    table = Table(Env.DATABASE.table)
    cfg = await table.select_one({"id": chat_id})
    if not cfg:
        await cb.answer(
            "Конфигурация не найдена. Введите /config, чтобы инициализировать."
        )
        return

    fake_message = types.Message(
        message_id=0,
        date=cb.message.date,
        chat=cb.message.chat,
        text="",
        from_user=cb.from_user,
    )
    if not await is_admin(fake_message, bot):
        await cb.answer("Только администраторы чата могут выполнить это действие")
        return

    if action == "history":
        if param == "custom":
            pending_actions[chat_id] = {"action": "set_history"}
            await cb.message.answer(
                "Введите желаемую длину контекста (число). Максимум 10 без Premium, 25 с Premium. Отправьте 'skip', чтобы отказаться."
            )
            await cb.answer()
            return

        try:
            value = int(param)
        except Exception:
            await cb.answer("Неправильное значение")
            return

        max_allowed = 25 if cfg.get("is_premium") else 10
        if value > max_allowed:
            await cb.answer(
                f"Этот чат не имеет премиума, максимальное разрешенное значение: {max_allowed} сообщений."
            )
            return

        await table.update({"id": chat_id}, {"history_maxlen": value})
        await cb.message.answer(f"Макс. длина контекста изменена на {value} сообщений.")
        await cb.answer()
        return

    if action == "prompt":
        if not cfg.get("is_premium"):
            await cb.answer("Изменение промпта доступно только для Premium чатов")
            return
        pending_actions[chat_id] = {"action": "set_prompt"}
        await cb.message.answer(
            "Введите новый промпт в чат (поменяет режим бота на 'CUSTOM'). Отправьте 'skip', чтобы отказаться."
        )
        await cb.answer()
        return

    if action == "mode":
        model_name = param.upper() if param else ""
        if model_name == "MODERATOR":
            await cb.answer("Модераторский режим нельзя установить через эту панель")
            return

        if model_name == "CUSTOM":
            default_prompt = DefaultModels.SMART.system_prompt
            current_prompt = cfg.get("prompt") or ""
            if not current_prompt or current_prompt == default_prompt:
                await cb.answer(
                    "Чтобы использовать кастомный режим, вы должны поменять промпт."
                )
                return

        await table.update({"id": chat_id}, {"bot_mode": model_name})
        await cb.message.answer(f"Режим бота изменен на {model_name}.")
        await cb.answer()
        return

    if action == "botname":
        pending_actions[chat_id] = {"action": "set_botname"}
        await cb.message.answer(
            "Отправьте новое имя бота (макс. 15 символов). Отправьте 'skip', чтобы отказаться."
        )
        await cb.answer()
        return

    if action == "openrouter":
        pending_actions[chat_id] = {"action": "set_openrouter"}
        await cb.message.answer(
            "Чтобы предоставить ключ OpenRouter, вставьте его в сообщение. Отправьте 'skip', чтобы отказаться."
        )
        await cb.answer()
        return

    if action == "show":
        text = keyboards.build_config_text(cfg)
        kb = keyboards.build_config_keyboard(cfg)
        await cb.message.answer(text, reply_markup=kb)
        await cb.answer()
        return


@base_router.message(lambda message: message.chat.id in pending_actions)
async def pending_action_receiver(message: types.Message, bot: Bot):
    chat_id = message.chat.id

    action_info = pending_actions.pop(chat_id)
    action = action_info.get("action")
    table = Table(Env.DATABASE.table)
    cfg = await table.select_one({"id": chat_id}) or {}

    if not await is_admin(message, bot):
        await message.reply(
            "❌ Только администраторы чата могут выполнить это действие"
        )
        return

    if message.text.strip().lower() == "skip":
        await message.reply("✅ Действие отменено.")
        return

    processor = PendingActionProcessor(table, cfg)
    reply, put_back = await processor.process(action, message)
    await message.reply(reply)
    if put_back:
        pending_actions[chat_id] = action_info

@base_router.message()
async def handle_all_messages(message: types.Message):
    # Dummy handler to ensure middleware runs for all messages
    pass