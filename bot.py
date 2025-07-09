import os
import asyncio
import importlib
import pkgutil
from datetime import datetime
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from modules.db import db, init_guests_table, init_visits_table
from modules.admin import startup as admin_startup
import modules.menu  # register /help
from modules.env import get_env

load_dotenv()

_format = "[%(asctime)s] %(levelname)s:%(name)s - %(message)s"
_datefmt = "%Y-%m-%d %H:%M:%S"
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(_format, _datefmt)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])

log = logging.getLogger(__name__)

TOKEN = get_env("BOT_TOKEN", required=True)
OWNER_ID = int(get_env("OWNER_ID", required=True))

bot = Bot(TOKEN)
dp = Dispatcher()
START_TIME = datetime.now()


@dp.message(Command("start"))
async def start_cmd(message: types.Message) -> None:
    parts = message.text.split() if message.text else []
    if message.from_user.id != OWNER_ID:
        if len(parts) == 1:
            await message.answer("🚫 Access denied.")
        return
    delta = datetime.now() - START_TIME
    days = delta.days
    hours = delta.seconds // 3600
    modules = [
        n for _, n, _ in pkgutil.iter_modules(["modules"]) if not n.startswith("_")
    ]
    mods = ", ".join(modules) if modules else "none"
    await message.answer(
        f"Status: OK\nup for {days}d {hours}h\nLoaded modules: {mods}\nbot core by @cha0skvlt"
    )


async def on_startup():
    """Connect DB and load routers from modules package."""
    await db.connect()
    await init_guests_table()
    await init_visits_table()
    await admin_startup()

    for _, name, _ in pkgutil.iter_modules(["modules"]):
        if name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"modules.{name}")
            router = getattr(module, "router", None)
            if router:
                dp.include_router(router)
        except Exception as e:
            log.exception("Failed to load module %s: %s", name, e)


async def on_shutdown() -> None:
    await db.close()
    log.info("db closed")
    await bot.session.close()
    log.info("bot session closed")


async def main():
    await on_startup()
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
