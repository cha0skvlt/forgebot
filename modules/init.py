import logging

from modules.db import db, init_guests_table, init_visits_table
from modules.admin import startup as admin_startup

log = logging.getLogger(__name__)


async def startup() -> None:
    await db.connect()
    await admin_startup()
    await init_guests_table()
    await init_visits_table()
    log.info("DB tables ensured")
