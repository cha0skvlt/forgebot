from __future__ import annotations
import os
import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from modules.db import db

router = Router()
log = logging.getLogger(__name__)


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
