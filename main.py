import asyncio
from aiogram import Dispatcher
from contextlib import suppress

import src.bot

from src.bot.moderator.routers import md_router
from src.bot.ai.routers import ai_router
from src.bot.base.routers import base_router
from src.bot.core.middlewares.ai_middleware import HistoryMiddleware
from src.logging.logging import init_aiogram_logging, get_debug_logger

init_aiogram_logging("logs/bot.txt")


async def main():
    debug = get_debug_logger().debug
    dp = Dispatcher()

    dp.include_router(ai_router)
    dp.include_router(md_router)
    dp.include_router(base_router)

    dp.message.middleware(HistoryMiddleware())

    print("Bot started")
    debug("Bot started")
    await dp.start_polling(src.bot.bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
