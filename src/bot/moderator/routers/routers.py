from src.bot.functions import is_admin, parse_time

from aiogram import Bot, Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress

md_router = Router()
md_router.message.filter(F.chat.type != "private") # Commands could use in groups

@md_router.message(Command("mute"))
async def func_mute(message: types.Message, command: CommandObject, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    date = parse_time(command.args)
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id, until_date=date, permissions=types.ChatPermissions(can_send_messages=False))
        await message.answer(f" Пользователь {mention} был заглушен.")

@md_router.message(Command("unmute"))
async def func_unmute(message: types.Message, bot: Bot):
    reply_message = message.reply_to_message 

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)
    
    await bot.restrict_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id, permissions=types.ChatPermissions(can_send_messages=True, can_send_other_messages=True))
    await message.answer(f" Все ограничения с пользователя {mention} были сняты.")

@md_router.message(Command("ban"))
async def func_ban(message: types.Message, command: CommandObject, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    date = parse_time(command.args)
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id, until_date=date)
        await message.answer(f"Пользователь {mention} заблокирован.")

@md_router.message(Command("unban"))
async def func_unban(message: types.Message, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id, only_if_banned=True)
        await message.answer(f"Пользователь {mention} разблокирован.")

@md_router.message(Command("kick"))
async def func_kick(message: types.Message, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id)
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id)
        await message.answer(f"Пользователь {mention} кикнут.")