from __future__ import annotations

import os
import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from datetime import date
import io
import qrcode
from dotenv import load_dotenv

from modules.db import db

router = Router()
log = logging.getLogger(__name__)


async def startup() -> None:
    load_dotenv()
    await db.execute("CREATE TABLE IF NOT EXISTS admins(user_id BIGINT PRIMARY KEY)")
    log.info("Admins table ensured")


def _owner_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        owner_id = int(os.environ.get("OWNER_ID", 0))
        if message.from_user and message.from_user.id == owner_id:
            return await func(message, *args, **kwargs)
        await message.answer("🚫 Access denied.")

    return wrapper


def _admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        owner_id = int(os.environ.get("OWNER_ID", "0"))
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
    url = f"t.me/{me.username}?start={uuid}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    await bot.send_photo(
        message.from_user.id,
        BufferedInputFile(buf.getvalue(), filename="qr.png"),
        caption=url,
    )
