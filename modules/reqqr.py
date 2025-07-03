from __future__ import annotations
import os
import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from datetime import date

from modules.db import db

router = Router()
log = logging.getLogger(__name__)


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


@router.message(Command("start"))
async def start_uuid(message: Message, bot: Bot) -> None:
    parts = message.text.split() if message.text else []
    if len(parts) != 2:
        return
    uuid = parts[1]
    row = await db.fetchrow("SELECT tg_id FROM guests WHERE uuid=$1", uuid)
    if not row:
        await message.answer("❌ Invalid QR code.")
        return
    if row["tg_id"]:
        await message.answer("You are already registered.")
        return
    await db.execute(
        "UPDATE guests SET tg_id=$1, name=$2, source='qr' WHERE uuid=$3",
        message.from_user.id,
        message.from_user.username,
        uuid,
    )
    channel_id = os.getenv("CHANNEL_ID")
    if channel_id:
        try:
            link = await bot.create_chat_invite_link(int(channel_id), member_limit=1)
            await bot.send_message(message.from_user.id, link.invite_link)
        except Exception as e:
            log.exception("invite failed: %s", e)
            await message.answer("Registered, but invite failed.")
            return
    await message.answer("✅ Registration complete.")


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
