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


@base_router.message(Command("start"))
async def func_start(message: types.Message):
    await message.reply(Config.BASE_PHRASES.START)


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
        await message.reply("Только администраторы чата могут выполнить это действие")
        return

    if message.text.strip().lower() == "skip":
        await message.reply("Действие отменено.")
        return

    if action == "set_history":
        try:
            value = int(message.text.strip())
        except Exception:
            pending_actions[chat_id] = action_info
            await message.reply(
                "Пожалуйста, введите положительное целое число, и попробуйте снова."
            )
            return
        max_allowed = 25 if cfg.get("is_premium") else 10
        if value > max_allowed:
            pending_actions[chat_id] = action_info
            await message.reply(
                f"Значение слишком больше, максимальное: {max_allowed} сообщений. Попробуйте снова"
            )
            return
        await table.update({"id": chat_id}, {"history_maxlen": value})
        await message_storage.ensure_chat(chat_id, maxlen=value)
        await message.reply(f"Длина контекста изменена на: {value} сообщений")
        return

    if action == "set_prompt":
        new_prompt = message.text.strip()
        if not new_prompt:
            pending_actions[chat_id] = action_info
            await message.reply("Промпт не может быть пустым. Попробуйте снова")
            return
        await table.update(
            {"id": chat_id}, {"prompt": new_prompt, "bot_mode": "CUSTOM"}
        )
        await message.reply("Промпт обновлен, и режим бота изменен на 'CUSTOM'")
        return

    if action == "set_botname":
        name = message.text.strip()
        if len(name) > 15:
            pending_actions[chat_id] = action_info
            await message.reply(
                "Имя слишком большое, максимум 15 символов. Попробуйте снова"
            )
            return
        await table.update({"id": chat_id}, {"bot_name": name})
        await message.reply(f"Имя бота изменено на '{name}'.")
        return

    if action == "set_openrouter":
        key = message.text.strip()
        if len(key) < 10:
            pending_actions[chat_id] = action_info
            await message.reply(
                "Предоставленный ключ выглядит слишком коротким; пожалуйста, перепроверьте и отправьте заново."
            )
            return
        await table.update({"id": chat_id}, {"openrouter_key": key})
        await message.reply("Ключ OpenRouter сохранен.")
        return

    await message.reply("Действие не распознано или срок действия уже истек.")
