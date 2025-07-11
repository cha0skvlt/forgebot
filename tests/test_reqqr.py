import os
import sys
import pathlib
import pytest

os.environ["OWNER_ID"] = "1"

os.environ["CHANNEL_ID"] = "-100123"
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import reqqr, admin, env



class DummyUser:
    def __init__(self, uid, username="name", first_name="first"):
        self.id = uid
        self.username = username
        self.first_name = first_name


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
    calls = {"update": None, "invite": None, "visits": 0}

    async def dummy_fetchrow(q, uuid):
        assert uuid == "good"
        return {"id": 1, "tg_id": None, "invited_at": None}

    async def dummy_execute(q, *args):
        if "invited_at" in q:
            calls["invite"] = args
        elif "UPDATE guests SET tg_id" in q:
            calls["update"] = args
        elif "INSERT INTO visits" in q:
            calls["visits"] += 1

    async def dummy_fetchval(q, *args):
        return calls["visits"]

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    os.environ["CHANNEL_ID"] = "-100123"
    env.CHANNEL_ID = "-100123"
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert calls["update"] == (42, "user", "good")
    assert calls["invite"] == (1,)
    assert msg.bot.created and msg.bot.sent
    assert msg.answers == ["✅ Registration complete. Согласие получено."]


@pytest.mark.asyncio
async def test_start_uuid_public(monkeypatch):
    calls = {"invite": None}

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": None, "invited_at": None}

    async def dummy_execute(q, *args):
        if "invited_at" in q:
            calls["invite"] = args

    async def dummy_fetchval(q, *args):
        return 1

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    os.environ["CHANNEL_ID"] = "@pub"
    env.CHANNEL_ID = "@pub"
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert msg.bot.sent == [(msg.from_user.id, "https://t.me/pub")]
    assert calls["invite"] == (1,)


@pytest.mark.asyncio
async def test_start_uuid_invite_error(monkeypatch):
    calls = {"invite": None}

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": None, "invited_at": None}

    async def dummy_execute(q, *args):
        if "invited_at" in q:
            calls["invite"] = args

    async def dummy_fetchval(q, *args):
        return 1

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    os.environ["CHANNEL_ID"] = "-100123"
    env.CHANNEL_ID = "-100123"

    async def fail_invite(*args, **kwargs):
        raise Exception("boom")

    msg = make_msg()
    msg.bot.create_chat_invite_link = fail_invite
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert not msg.bot.sent
    assert msg.answers[-1] == "Registered, but invite failed."
    assert calls["invite"] is None


@pytest.mark.asyncio
async def test_start_uuid_no_links(monkeypatch):
    warnings = []

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": None, "invited_at": None}

    async def dummy_execute(q, *args):
        pass

    async def dummy_fetchval(q, *args):
        return 1

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(reqqr.log, "warning", lambda msg: warnings.append(msg))
    os.environ.pop("CHANNEL_ID", None)
    env.CHANNEL_ID = None
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert not msg.bot.sent
    assert warnings


@pytest.mark.asyncio
async def test_start_uuid_name_fallback(monkeypatch):
    calls = {"update": None, "visits": 0}

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": None, "invited_at": None}

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
    msg = make_msg()
    msg.from_user.username = None
    msg.from_user.first_name = "First"
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert calls["update"] == (42, "First", "good")


@pytest.mark.asyncio
async def test_start_uuid_already_invited(monkeypatch):
    calls = {"update": None, "invite": False}

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": None, "invited_at": "2025"}

    async def dummy_execute(q, *args):
        if "invited_at" in q:
            calls["invite"] = True
        elif "UPDATE guests SET tg_id" in q:
            calls["update"] = args

    async def dummy_fetchval(q, *args):
        return 1

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    os.environ["CHANNEL_ID"] = "-100123"
    env.CHANNEL_ID = "-100123"
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert calls["update"] == (42, "user", "good")
    assert not calls["invite"]
    assert not msg.bot.sent


@pytest.mark.asyncio
async def test_start_uuid_repeat(monkeypatch):
    visits = 1

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": 42, "invited_at": '2025'}

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
async def test_start_uuid_registered_first_visit(monkeypatch):
    calls = {"update": 0, "visits": 0}

    async def dummy_fetchrow(q, uuid):
        return {"id": 1, "tg_id": 42, "invited_at": '2025'}

    async def dummy_execute(q, *args):
        if "UPDATE guests" in q:
            calls["update"] += 1
        elif "INSERT INTO visits" in q:
            calls["visits"] += 1

    async def dummy_fetchval(q, *args):
        return calls["visits"]

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    msg = make_msg()
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert calls["update"] == 0
    assert calls["visits"] == 1
    assert msg.answers == ["Это уже 1-е посещение"]
    assert not msg.bot.created and not msg.bot.sent


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
    calls = {"guest": None, "visits": 0}

    async def dummy_fetchrow(q, uid):
        return {"user_id": uid}

    async def dummy_fetchval(q, *args):
        if "gen_random_uuid" in q:
            return "uuid"
        return 1

    async def dummy_execute(q, *args):
        if "INSERT INTO visits" in q:
            calls["visits"] += 1
        else:
            calls["guest"] = args

    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    monkeypatch.setattr(reqqr.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(reqqr.db, "execute", dummy_execute)
    msg = make_msg("/reg Name, +79998887766, 1990-01-01")
    await reqqr.reg_guest(msg)
    assert calls["guest"] == (
        "uuid",
        "Name",
        "+79998887766",
        "1990-01-01",
    )
    assert calls["visits"] == 1
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


@pytest.mark.asyncio
async def test_start_uuid_owner_skip(monkeypatch):
    called = False

    async def dummy_fetchrow(q, uuid):
        nonlocal called
        called = True

        return {"id": 1, "tg_id": None, "invited_at": None}


    monkeypatch.setattr(reqqr.db, "fetchrow", dummy_fetchrow)
    msg = make_msg()
    msg.from_user.id = 1
    await reqqr.start_uuid(msg, bot=msg.bot)
    assert not called
    assert msg.answers == []
