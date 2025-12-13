from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.ai.service.default_models import DefaultModels


def build_config_text(cfg: dict) -> str:
	"""Return a human-friendly text representation of the chat config."""
	lines = []
	lines.append(f"Макс. длина контекста: {cfg.get('history_maxlen')} (соо.)")
	lines.append(f"Premium: {'Есть' if cfg.get('is_premium') else 'Нет'}")
	lines.append(f"Имя бота: {cfg.get('bot_name') or 'Гриффель'}")
	lines.append(f"Режим бота: {cfg.get('bot_mode') or '(не установлен)'}")
	lines.append(f"Правила чата: {"(установлены)" if cfg.get('chat_rules') else '(не установлены)'}")
	lines.append(f"Ключ OpenRouter: {'Установлен' if cfg.get('openrouter_key') else 'Не установлен'}")
	return "\n".join(lines)


def build_config_keyboard(cfg: dict = {}) -> InlineKeyboardMarkup:
	"""Build an InlineKeyboardMarkup for chat configuration actions.

	Buttons use callback data prefixed with 'cfg:'.
	"""
	# Build explicit rows to ensure proper InlineKeyboardMarkup structure
	rows = []

	# Show / refresh
	rows.append([InlineKeyboardButton(text="Обновить", callback_data="cfg:show")])

	# Prompt (requires premium to actually accept changes)
	rows.append([InlineKeyboardButton(text="Изменить базовый промпт", callback_data="cfg:prompt")])

	# Modes (exclude MODERATOR)
	modes = [m for m in DefaultModels.__dict__ if m.isupper() and m != 'MODERATOR']
	mode_buttons = [InlineKeyboardButton(text=m.capitalize(), callback_data=f"cfg:mode:{m}") for m in modes]
	# add a custom option that requires a custom prompt
	mode_buttons.append(InlineKeyboardButton(text="Custom", callback_data="cfg:mode:CUSTOM"))
	# place modes in one or two rows of up to 3 buttons
	row = []
	for i, btn in enumerate(mode_buttons, 1):
		row.append(btn)
		if i % 3 == 0:
			rows.append(row)
			row = []
	if row:
		rows.append(row)

	# History quick options and custom
	rows.append([
		InlineKeyboardButton(text="Контекст: 1 соо.", callback_data="cfg:history:1"),
		InlineKeyboardButton(text="Контекст: 5 соо.", callback_data="cfg:history:5"),
	])
	rows.append([
		InlineKeyboardButton(text="Контекст: 10 соо.", callback_data="cfg:history:10"),
		InlineKeyboardButton(text="Контекст: кастомный", callback_data="cfg:history:custom"),
	])

	# Bot name and openrouter
	rows.append([InlineKeyboardButton(text="Поставить имя бота", callback_data="cfg:botname")])
	rows.append([InlineKeyboardButton(text="Поставить ключ OpenRouter", callback_data="cfg:openrouter")])

	return InlineKeyboardMarkup(inline_keyboard=rows)

