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
    
    mention = reply_message.from_user

    bot_user = await bot.get_me()
    if mention.id == bot_user.id:
        await message.reply("Я не могу заглушить самого себя!")
        return
    
    date = parse_time(command.args)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=mention.id,
            permissions=types.ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            ), until_date=date
        )
        await message.reply(f"Пользователь {mention.mention_markdown(reply_message.from_user.first_name)} заглушен до {date.strftime('%H:%M %d.%m.%Y')}")

@md_router.message(Command("unmute"))
async def func_unmute(message: types.Message, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    mention = reply_message.from_user

    bot_user = await bot.get_me()
    if mention.id == bot_user.id:
        await message.reply("Я не могу применить эту команду на самого себя!")
        return
    
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=mention.id,
            permissions=types.ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply(f"Пользователь {mention.mention_markdown(reply_message.from_user.first_name)} больше не заглушен.")

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
        await message.answer(f"Пользователь **{mention}** заблокирован.")

@md_router.message(Command("unban"))
async def func_unban(message: types.Message, bot: Bot):
    reply_message = message.reply_to_message

    if not reply_message or not await is_admin(message, bot):
        await message.reply("Произошла ошибка!")
        return
    
    mention = reply_message.from_user.mention_markdown(reply_message.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=reply_message.from_user.id, only_if_banned=True)
        await message.answer(f"Пользователь **{mention}** разблокирован.")

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
        await message.answer(f"Пользователь **{mention}** кикнут.")