from aiogram import Bot
from aiogram.types import Message, ChatPermissions
from aiogram.filters import CommandObject
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress

from src.bot.functions import is_admin, parse_time


class ModeratorComands:
    @staticmethod
    async def mute_user(message: Message, command: CommandObject, bot: Bot):
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
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                ),
                until_date=date,
            )
            await message.reply(
                f"Пользователь {mention.mention_markdown(reply_message.from_user.first_name)} заглушен до {date.strftime('%H:%M %d.%m.%Y')}"
            )

    @staticmethod
    async def unmute_user(message: Message, bot: Bot):
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
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            await message.reply(
                f"Пользователь {mention.mention_markdown(reply_message.from_user.first_name)} больше не заглушен."
            )

    @staticmethod
    async def ban_user(message: Message, command: CommandObject, bot: Bot):
        reply_message = message.reply_to_message

        if not reply_message or not await is_admin(message, bot):
            await message.reply("Произошла ошибка!")
            return

        date = parse_time(command.args)
        mention = reply_message.from_user.mention_markdown(
            reply_message.from_user.first_name
        )

        with suppress(TelegramBadRequest):
            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=reply_message.from_user.id,
                until_date=date,
            )
            await message.answer(f"Пользователь **{mention}** заблокирован.")

    @staticmethod
    async def unban_user(message: Message, bot: Bot):
        reply_message = message.reply_to_message

        if not reply_message or not await is_admin(message, bot):
            await message.reply("Произошла ошибка!")
            return

        mention = reply_message.from_user.mention_markdown(
            reply_message.from_user.first_name
        )

        with suppress(TelegramBadRequest):
            await bot.unban_chat_member(
                chat_id=message.chat.id,
                user_id=reply_message.from_user.id,
                only_if_banned=True,
            )
            await message.answer(f"Пользователь **{mention}** разблокирован.")

    @staticmethod
    async def kick_user(message: Message, bot: Bot):
        reply_message = message.reply_to_message

        if not reply_message or not await is_admin(message, bot):
            await message.reply("Произошла ошибка!")
            return

        mention = reply_message.from_user.mention_markdown(
            reply_message.from_user.first_name
        )

        with suppress(TelegramBadRequest):
            await bot.ban_chat_member(
                chat_id=message.chat.id, user_id=reply_message.from_user.id
            )
            await bot.unban_chat_member(
                chat_id=message.chat.id, user_id=reply_message.from_user.id
            )
            await message.answer(f"Пользователь **{mention}** кикнут.")

    @staticmethod
    async def warn_user(message: Message, bot: Bot):
        # TODO Сделать варн
        ...

    @staticmethod
    async def mute_with_id(chat_id: int, user_id: int, bot: Bot):
        with suppress(TelegramBadRequest):
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                ),
                until_date=parse_time(),
            )

    @staticmethod
    async def unmute_with_id(chat_id: int, user_id: int, bot: Bot):
        with suppress(TelegramBadRequest):
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )

    @staticmethod
    async def ban_with_id(chat_id: int, user_id: int, bot: Bot):
        with suppress(TelegramBadRequest):
            await bot.ban_chat_member(
                chat_id=chat_id, user_id=user_id, until_date=parse_time()
            )

    @staticmethod
    async def unban_with_id(chat_id: int, user_id: int, bot: Bot):
        with suppress(TelegramBadRequest):
            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=True,
            )

    @staticmethod
    async def kick_with_id(chat_id: int, user_id: int, bot: Bot):
        with suppress(TelegramBadRequest):
            await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)

    @staticmethod
    async def warn_with_id(chat_id: int, user_id: int, bot: Bot):
        # TODO Сделать варн
        ...
