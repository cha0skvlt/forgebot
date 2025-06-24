import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import admin

os.environ["OWNER_ID"] = "1"


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
