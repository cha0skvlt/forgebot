import os
import asyncio
import importlib
import pkgutil
from datetime import datetime
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from modules.db import db
from modules.admin import startup as admin_startup

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

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

if not OWNER_ID:
    raise RuntimeError("OWNER_ID not set")

bot = Bot(TOKEN)
dp = Dispatcher()
START_TIME = datetime.now()


@dp.message(Command("start"))
async def start_cmd(message: types.Message) -> None:
    if message.from_user.id != OWNER_ID:
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
    await admin_startup()  # create tables

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
