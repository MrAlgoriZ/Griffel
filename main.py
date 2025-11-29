import asyncio
from aiogram import Dispatcher

import src.bot

from src.bot.moderator.routers import md_router
from src.bot.ai.routers import ai_router
from src.bot.base.routers import base_router

async def main():
    dp = Dispatcher()
    
    dp.include_router(base_router)
    dp.include_router(md_router)
    dp.include_router(ai_router)
    
    await dp.start_polling(src.bot.bot)

if __name__ == "__main__":
    asyncio.run(main())