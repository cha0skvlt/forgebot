import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import reqqr


class DummyUser:
    def __init__(self, uid, username="name"):
        self.id = uid
        self.username = username


class DummyBot:
    def __init__(self):
        self.created = []
        self.sent = []

    async def create_chat_invite_link(self, chat_id, member_limit=1):
        self.created.append((chat_id, member_limit))
        return type("Link", (), {"invite_link": "link"})()

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


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
    called = {}

    async def dummy_fetchrow(q, uuid):
        assert uuid == "good"
        return {"tg_id": None}

    async def dummy_execute(q, *args):
        called["exec"] = args

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    os.environ["CHANNEL_ID"] = "123"
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert called["exec"] == (42, "user", "good")
    assert msg.bot.created and msg.bot.sent
    assert msg.answers == ["✅ Registration complete."]


@pytest.mark.asyncio
async def test_start_uuid_duplicate(monkeypatch):
    async def dummy_fetchrow(q, uuid):
        return {"tg_id": 42}

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert msg.answers == ["You are already registered."]


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

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    msg = make_msg("/reg Name, +79998887766, 1990-01-01")
    await reqqr.reg_guest(msg)
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

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    msg = make_msg("/reg Name, 12345, 1990-01-01")
    await reqqr.reg_guest(msg)
    assert msg.answers == ["Invalid phone"]


@pytest.mark.asyncio
async def test_reg_invalid_date(monkeypatch):
    async def dummy_fetchrow(q, a):
        return {"user_id": a}

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    msg = make_msg("/reg Name, +79998887766, 1990-13-01")
    await reqqr.reg_guest(msg)
    assert msg.answers == ["Invalid date"]

