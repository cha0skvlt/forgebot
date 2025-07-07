from __future__ import annotations
import logging
from datetime import date
import io
import qrcode

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from modules.db import db
from modules.env import get_env

router = Router()
log = logging.getLogger(__name__)


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
        channel_id = get_env("CHANNEL_ID")
        if channel_id:
            try:
                link = await bot.create_chat_invite_link(int(channel_id), member_limit=1)
                await bot.send_message(message.from_user.id, link.invite_link)
            except Exception as e:
                log.exception("invite failed: %s", e)
                await message.answer("Registered, but invite failed.")
        else:
            log.warning("CHANNEL_ID not set")
    else:
        await message.answer(f"Это уже {count}-е посещение")


@router.message(Command("reg"))
@_admin_only
async def reg_guest(message: Message) -> None:
    parts = message.text.split(" ", 1)
    if len(parts) != 2:
        await message.answer

