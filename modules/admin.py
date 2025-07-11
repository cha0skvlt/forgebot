from __future__ import annotations

import os
import logging
import pkgutil
from datetime import date, datetime
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from modules.qr import make_qr_link
from modules.db import db
from modules.env import get_env

router = Router()
log = logging.getLogger(__name__)
START_TIME = datetime.now()


async def startup() -> None:
    await db.execute("CREATE TABLE IF NOT EXISTS admins(user_id BIGINT PRIMARY KEY)")
    log.info("Admins table ensured")


def _owner_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        owner_id = int(get_env("OWNER_ID", required=True))
        if message.from_user and message.from_user.id == owner_id:
            return await func(message, *args, **kwargs)
        await message.answer("🚫 Access denied.")

    return wrapper


def _admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        owner_id = int(get_env("OWNER_ID", required=True))
        if uid == owner_id:
            return await func(message, *args, **kwargs)
        row = await db.fetchrow("SELECT 1 FROM admins WHERE user_id=$1", uid)
        if row:
            return await func(message, *args, **kwargs)
        await message.answer("🚫 Access denied.")

    return wrapper


@router.message(Command("add_admin"))
@_owner_only
async def add_admin(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /add_admin <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    await db.execute(
        "INSERT INTO admins(user_id) VALUES($1) ON CONFLICT DO NOTHING", uid
    )
    log.info("Added admin %s", uid)
    await message.answer(f"Added admin {uid}")


@router.message(Command("rm_admin"))
@_owner_only
async def rm_admin(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /rm_admin <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    await db.execute("DELETE FROM admins WHERE user_id=$1", uid)
    log.info("Removed admin %s", uid)
    await message.answer(f"Removed admin {uid}")


@router.message(Command("list_admin"))
@_owner_only
async def list_admin(message: Message) -> None:
    rows = await db.fetch("SELECT user_id FROM admins")
    admins = [str(r["user_id"]) for r in rows]
    text = ", ".join(admins) if admins else "No admins."
    log.info("Listed admins: %s", text)
    await message.answer(text)


@router.message(Command("reg"))
@_admin_only
async def reg_guest(message: Message) -> None:
    parts = message.text.split(" ", 1)
    if len(parts) != 2:
        await message.answer("Usage: /reg ФИО, телефон, YYYY-MM-DD")
        return
    fields = [f.strip() for f in parts[1].split(",")]
    if len(fields) != 3:
        await message.answer("Invalid format")
        return
    name, phone, dob_str = fields
    if not (phone.startswith("+7") or phone.startswith("8")):
        await message.answer("Invalid phone")
        return
    try:
        date.fromisoformat(dob_str)
    except ValueError:
        await message.answer("Invalid date")
        return
    uuid = await db.fetchval("SELECT gen_random_uuid()")
    await db.execute(
        "INSERT INTO guests(uuid, name, phone, dob, source) VALUES($1,$2,$3,$4,'manual')",
        uuid,
        name,
        phone,
        dob_str,
    )
    await message.answer("✅ Guest registered.")


@router.message(Command("genqr"))
@_admin_only
async def genqr_cmd(message: Message, bot: Bot) -> None:
    uuid = await db.fetchval("SELECT gen_random_uuid()")
    await db.execute("INSERT INTO guests(uuid, source) VALUES($1, 'qr')", uuid)
    me = await bot.get_me()
    url, data = make_qr_link(uuid, me.username)
    await bot.send_photo(
        message.from_user.id,
        BufferedInputFile(data, filename="qr.png"),
        caption=url,
    )



@router.message(Command("search_guest"))
@_admin_only
async def search_guest(message: Message) -> None:
    parts = message.text.split(" ", 1)
    if len(parts) != 2:
        await message.answer("Usage: /search_guest <query>")
        return
    query = f"%{parts[1].strip()}%"
    rows = await db.fetch(
        "SELECT name, phone, dob FROM guests WHERE name ILIKE $1 OR phone ILIKE $1 LIMIT 10",
        query,
    )
    if not rows:
        await message.answer("❌ No guests found.")
        return
    lines = [f"{r['name']}, {r['phone']}, {r['dob']}" for r in rows]
    await message.answer("\n".join(lines))

@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    owner_id = int(get_env("OWNER_ID", required=True))
    if message.from_user.id != owner_id:
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

