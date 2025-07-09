import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import menu, admin

os.environ["OWNER_ID"] = "1"

class DummyUser:
    def __init__(self, uid):
        self.id = uid

class DummyMessage:
    def __init__(self, uid=1):
        self.text = "/help"
        self.from_user = DummyUser(uid)
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


def make_msg(uid=1):
    return DummyMessage(uid)


@pytest.mark.asyncio
async def test_help_owner(monkeypatch):
    msg = make_msg(1)
    await menu.help_cmd(msg)
    assert msg.answers and msg.answers[0].startswith("\N{LOCK WITH INK PEN}")


@pytest.mark.asyncio
async def test_help_denied(monkeypatch):
    async def no_admin(*args, **kwargs):
        return None
    monkeypatch.setattr(admin.db, "fetchrow", no_admin)
    msg = make_msg(2)
    await menu.help_cmd(msg)
    assert msg.answers == ["🚫 Access denied."]
