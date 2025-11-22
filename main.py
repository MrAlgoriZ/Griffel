import asyncio
from aiogram import Dispatcher

import src.bot

from src.bot.moderator.routers.routers import md_router
# from src.bot.ai.router_handler import ai_rt

async def main():
    dp = Dispatcher()
    dp.include_router(md_router)
    # dp.include_router(ai_rt)
    await dp.start_polling(src.bot.bot)


if __name__ == "__main__":
    asyncio.run(main())