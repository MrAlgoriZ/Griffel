import asyncio
from aiogram import Dispatcher
from contextlib import suppress

import src.bot

from src.bot.moderator.routers import md_router
from src.bot.ai.routers import ai_router, HistoryMiddleware
from src.bot.base.routers import base_router

async def main():
    dp = Dispatcher()
    
    dp.include_router(base_router)
    dp.include_router(md_router)
    dp.include_router(ai_router)

    dp.message.middleware(HistoryMiddleware())
    
    await dp.start_polling(src.bot.bot)

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())