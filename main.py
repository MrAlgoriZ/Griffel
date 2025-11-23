import asyncio
from aiogram import Dispatcher

import src.bot

from src.bot.moderator.routers.routers import md_router
from src.bot.ai.routers.routers import ai_router

async def main():
    dp = Dispatcher()
    
    dp.include_router(md_router)
    dp.include_router(ai_router)
    
    await dp.start_polling(src.bot.bot)

if __name__ == "__main__":
    asyncio.run(main())