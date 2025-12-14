from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.ai.service.default_models import DefaultModels


def build_config_text(cfg: dict) -> str:
    lines = []
    lines.append(f"Макс. длина контекста: {cfg.get('history_maxlen')} (соо.)")
    lines.append(f"Premium: {'Есть' if cfg.get('is_premium') else 'Нет'}")
    lines.append(f"Режим бота: {cfg.get('bot_mode') or '(не установлен)'}")
    lines.append(
        f"Правила чата: {'(установлены)' if cfg.get('chat_rules') else '(не установлены)'}"
    )
    lines.append(
        f"Ключ OpenRouter: {'Установлен' if cfg.get('openrouter_key') else 'Не установлен'}"
    )
    return "\n".join(lines)


def build_config_keyboard(cfg: dict = {}) -> InlineKeyboardMarkup:
    rows = []

    rows.append([InlineKeyboardButton(text="Обновить", callback_data="cfg:show")])

    rows.append(
        [
            InlineKeyboardButton(
                text="Изменить базовый промпт", callback_data="cfg:prompt"
            )
        ]
    )

    modes = [m for m in DefaultModels.__dict__ if m.isupper() and m != "MODERATOR"]
    mode_buttons = [
        InlineKeyboardButton(text=m.capitalize(), callback_data=f"cfg:mode:{m}")
        for m in modes
    ]

    mode_buttons.append(
        InlineKeyboardButton(text="Custom", callback_data="cfg:mode:CUSTOM")
    )

    row = []
    for i, btn in enumerate(mode_buttons, 1):
        row.append(btn)
        if i % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append(
        [
            InlineKeyboardButton(
                text="Контекст: 1 соо.", callback_data="cfg:history:1"
            ),
            InlineKeyboardButton(
                text="Контекст: 5 соо.", callback_data="cfg:history:5"
            ),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text="Контекст: 10 соо.", callback_data="cfg:history:10"
            ),
            InlineKeyboardButton(
                text="Контекст: кастомный", callback_data="cfg:history:custom"
            ),
        ]
    )

    rows.append(
        [
            InlineKeyboardButton(
                text="Поставить ключ OpenRouter", callback_data="cfg:openrouter"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)
