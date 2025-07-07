import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from modules.db import db
from modules.admin import _admin_only

router = Router()
log = logging.getLogger(__name__)


@router.message(Command("report"))
@_admin_only
async def report_cmd(message: Message) -> None:
    total_guests = await db.fetchval("SELECT COUNT(*) FROM guests")
    unique_week = await db.fetchval(
        "SELECT COUNT(DISTINCT guest_id) FROM visits WHERE ts >= now() - interval '7 days'"
    )
    unique_month = await db.fetchval(
        "SELECT COUNT(DISTINCT guest_id) FROM visits WHERE ts >= date_trunc('month', now())"
    )
    total_visits = await db.fetchval("SELECT COUNT(*) FROM visits")
    repeat_visitors = await db.fetchval(
        "SELECT COUNT(*) FROM (SELECT guest_id FROM visits GROUP BY guest_id HAVING COUNT(*) > 1) t"
    )
    rows = await db.fetch(
        "SELECT g.name, COUNT(*) AS c FROM visits v JOIN guests g ON g.id=v.guest_id "
        "GROUP BY g.name ORDER BY c DESC LIMIT 3"
    )
    top = ", ".join(f"{r['name'] or '-'}-{r['c']}" for r in rows)
    text = (
        f"Всего гостей: {total_guests}\n"
        f"Уникальных за неделю: {unique_week}\n"
        f"Уникальных за месяц: {unique_month}\n"
        f"Всего визитов: {total_visits}\n"
        f"Повторных гостей: {repeat_visitors}\n"
        f"Топ гости: {top}"
    )
    await message.answer(text)
