import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN
from app.db import init_db
from app.scheduler import scheduler
from handlers import common, auth, drivers, consumers, support, orders

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common.router)
    dp.include_router(auth.router)
    dp.include_router(drivers.router)
    dp.include_router(consumers.router)
    dp.include_router(support.router)
    dp.include_router(orders.router)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
