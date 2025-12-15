from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from src.bot.moderator.commands import ModeratorComands

md_router = Router()
md_router.message.filter(F.chat.type != "private")


@md_router.message(Command("mute"))
async def func_mute(message: Message, command: CommandObject, bot: Bot):
    await ModeratorComands.mute_user(message, command, bot)


@md_router.message(Command("unmute"))
async def func_unmute(message: Message, bot: Bot):
    await ModeratorComands.unmute_user(message, bot)


@md_router.message(Command("ban"))
async def func_ban(message: Message, command: CommandObject, bot: Bot):
    await ModeratorComands.ban_user(message, command, bot)


@md_router.message(Command("unban"))
async def func_unban(message: Message, bot: Bot):
    await ModeratorComands.unban_user(message, bot)


@md_router.message(Command("kick"))
async def func_kick(message: Message, bot: Bot):
    await ModeratorComands.kick_user(message, bot)
