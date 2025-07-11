import os
import sys
import pathlib
import pytest
from datetime import datetime

os.environ["OWNER_ID"] = "1"
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import admin


class DummyUser:
    def __init__(self, user_id):
        self.id = user_id


class DummyMessage:
    def __init__(self, text):
        self.text = text
        self.from_user = DummyUser(1)
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


def make_msg(text: str):
    return DummyMessage(text)


@pytest.mark.asyncio
async def test_add_admin_invalid(monkeypatch):
    called = False

    async def dummy_execute(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(admin.db, "execute", dummy_execute)
    msg = make_msg("/add_admin abc")
    await admin.add_admin(msg)
    assert msg.answers == ["Invalid user ID"]
    assert not called


@pytest.mark.asyncio
async def test_rm_admin_invalid(monkeypatch):
    called = False

    async def dummy_execute(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(admin.db, "execute", dummy_execute)
    msg = make_msg("/rm_admin abc")
    await admin.rm_admin(msg)
    assert msg.answers == ["Invalid user ID"]
    assert not called


def test_admin_loads():
    import importlib
    import modules.admin as admin_mod
    importlib.reload(admin_mod)

@pytest.mark.asyncio
async def test_start_owner(monkeypatch):
    monkeypatch.setattr(admin, "START_TIME", datetime.now())
    monkeypatch.setattr(admin.pkgutil, "iter_modules", lambda *_: [])
    msg = make_msg("/start")
    await admin.start_cmd(msg)
    assert msg.answers and msg.answers[0].startswith("Status: OK")

