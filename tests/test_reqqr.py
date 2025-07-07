import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import reqqr, admin


class DummyUser:
    def __init__(self, uid, username="name"):
        self.id = uid
        self.username = username


class DummyBot:
    def __init__(self):
        self.created = []
        self.sent = []
        self.photos = []

    async def create_chat_invite_link(self, chat_id, member_limit=1):
        self.created.append((chat_id, member_limit))
        return type("Link", (), {"invite_link": "link"})()

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))

    async def send_photo(self, chat_id, photo, caption=None):
        self.photos.append((chat_id, photo, caption))

    async def get_me(self):
        return type("Me", (), {"username": "bot"})()


class DummyMessage:
    def __init__(self, text):
        self.text = text
        self.answers = []
        self.from_user = DummyUser(42, "user")
        self.bot = DummyBot()

    async def answer(self, text):
        self.answers.append(text)


def make_msg(text="/start good"):
    return DummyMessage(text)


@pytest.mark.asyncio
async def test_start_uuid_new(monkeypatch):
    calls = {"update": None, "visits": 0}

    async def dummy_fetchrow(q, uuid):
        assert uuid == "good"
        return {"id": 1, "tg_id": None}

    async def dummy_execute(q, *args):
        if "UPDATE guests" in q:
            calls["update"] = args
        elif "INSERT INTO visits" in q:
            calls["visits"] += 1

    async def dummy_fetchval(q, *args):
        return calls["visits"]

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    os.environ["CHANNEL_ID"] = "123"
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert calls["update"] == (42, "user", "good")
    assert msg.bot.created and msg.bot.sent
    assert msg.answers == ["✅ Registration complete. Согласие получено."]


@pytest.mark.asyncio
async def test_start_uuid_repeat(monkeypatch):
    visits = 1

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": 42}

    async def dummy_execute(q, *args):
        nonlocal visits
        if "INSERT INTO visits" in q:
            visits += 1

    async def dummy_fetchval(q, *args):
        return visits

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert msg.answers == ["Это уже 2-е посещение"]


@pytest.mark.asyncio
async def test_start_uuid_invalid(monkeypatch):
    async def dummy_fetchrow(q, uuid):
        return None

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    msg = make_msg("/start bad")
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert msg.answers == ["❌ Invalid QR code."]


@pytest.mark.asyncio
async def test_reg_success(monkeypatch):
    called = {}

    async def dummy_fetchrow(q, uid):
        return {"user_id": uid}

    async def dummy_fetchval(q):
        return "uuid"

    async def dummy_execute(q, *args):
        called["exec"] = args

    monkeypatch.setattr(admin.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(admin.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(admin.db, "execute", dummy_execute)
    msg = make_msg("/reg Name, +79998887766, 1990-01-01")
    await admin.reg_guest(msg)
    assert called["exec"] == (
        "uuid",
        "Name",
        "+79998887766",
        "1990-01-01",
    )
    assert msg.answers == ["✅ Guest registered."]


@pytest.mark.asyncio
async def test_reg_invalid_phone(monkeypatch):
    async def dummy_fetchrow(q, a):
        return {"user_id": a}

    monkeypatch.setattr(admin.db, "fetchrow", dummy_fetchrow)
    msg = make_msg("/reg Name, 12345, 1990-01-01")
    await admin.reg_guest(msg)
    assert msg.answers == ["Invalid phone"]


@pytest.mark.asyncio
async def test_reg_invalid_date(monkeypatch):
    async def dummy_fetchrow(q, a):
        return {"user_id": a}

    monkeypatch.setattr(admin.db, "fetchrow", dummy_fetchrow)
    msg = make_msg("/reg Name, +79998887766, 1990-13-01")
    await admin.reg_guest(msg)
    assert msg.answers == ["Invalid date"]


@pytest.mark.asyncio
async def test_genqr(monkeypatch):
    async def dummy_fetchrow(q, uid):
        return {"user_id": uid}

    async def dummy_fetchval(q):
        return "uuid"

    async def dummy_execute(q, uuid):
        assert uuid == "uuid"

    def dummy_make_qr(uuid, username):
        assert uuid == "uuid"
        assert username == "bot"
        return "t.me/bot?start=uuid", b"img"

    monkeypatch.setattr(admin.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(admin.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(admin.db, "execute", dummy_execute)
    monkeypatch.setattr(admin, "make_qr_link", dummy_make_qr)
    msg = make_msg("/genqr")
    await admin.genqr_cmd(msg, bot=msg.bot)
    assert msg.bot.photos
    chat_id, photo, caption = msg.bot.photos[0]
    assert chat_id == msg.from_user.id
    assert caption == "t.me/bot?start=uuid"
