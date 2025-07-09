from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from modules.admin import _admin_only

router = Router()

@router.message(Command("help"))
@_admin_only
async def help_cmd(message: Message) -> None:
    await message.answer(
        "\N{LOCK WITH INK PEN} Admin commands:\n"
        "- /add_admin \u2014 grant admin rights by ID\n"
        "- /rm_admin \u2014 revoke admin rights by ID\n"
        "- /list_admin \u2014 show current admins\n"
        "- /genqr \u2014 generate a shared QR code\n"
        "- /reg \u2014 manually register a guest\n"
        "- /report \u2014 show guest summary"
    )
