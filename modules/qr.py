from __future__ import annotations

import io
import qrcode


def make_qr_link(uuid: str, bot_username: str) -> tuple[str, bytes]:
    url = f"t.me/{bot_username}?start={uuid}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return url, buf.getvalue()
