from __future__ import annotations
import os
import logging
from datetime import date
import io
import qrcode

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

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
    row = await db.fetchrow("SELECT id, tg_id FROM guests WHERE uuid=$1", uuid)
    if not row:
        await message.answer("❌ Invalid QR code.")
        return
    guest_id = row["id"]
    if row["tg_id"] is None:
        name = message.from_user.username or message.from_user.first_name
        await db.execute(
            "UPDATE guests SET tg_id=$1, name=$2, source='qr', agreed_at=now() WHERE uuid=$3",
            message.from_user.id,
            name,
            uuid,
        )
        await message.answer("✅ Registration complete. Согласие получено.")
    await db.execute("INSERT INTO visits(guest_id) VALUES($1)", guest_id)
    count = await db.fetchval("SELECT COUNT(*) FROM visits WHERE guest_id=$1", guest_id)
    if count == 1:
        channel_id = os.getenv("CHANNEL_ID")
        if channel_id:
            try:
                link = await bot.create_chat_invite_link(int(channel_id), member_limit=1)
                await bot.send_message(message.from_user.id, link.invite_link)
            except Exception as e:
                log.exception("invite failed: %s", e)
                await message.answer("Registered, but invite failed.")
    else:
        await message.answer(f"Это уже {count}-е посещение")


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
    guest_id = await db.fetchval("SELECT id FROM guests WHERE uuid=$1", uuid)
    await db.execute("INSERT INTO visits(guest_id) VALUES($1)", guest_id)
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
