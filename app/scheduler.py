from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from .db import log_event
from .i18n import T

scheduler = AsyncIOScheduler()

async def remind_driver(bot: Bot, order_id: int, driver_id: int):
    msg = await T(driver_id, "reminder_driver_msg")
    await bot.send_message(driver_id, msg.format(id=order_id))
    await log_event(order_id, "reminder_sent")

def schedule_driver_reminder(bot: Bot, order_id: int, driver_id: int):
    scheduler.add_job(remind_driver, "interval", hours=1, args=[bot, order_id, driver_id], id=f"remind_{order_id}")

def cancel_reminder(order_id: int):
    job_id = f"remind_{order_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

