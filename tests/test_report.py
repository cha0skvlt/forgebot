import os
import sys
import pathlib
import pytest

os.environ["OWNER_ID"] = "1"
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import report


class DummyUser:
    def __init__(self, uid=1):
        self.id = uid


class DummyMessage:
    def __init__(self, text="/report"):
        self.text = text
        self.from_user = DummyUser()
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


def make_msg(text="/report"):
    return DummyMessage(text)


@pytest.mark.asyncio
async def test_report(monkeypatch):
    async def dummy_fetchval(query):
        if "FROM guests" in query:
            return 10
        if "7 days" in query:
            return 5
        if "date_trunc" in query:
            return 7
        if "COUNT(*) FROM visits" in query:
            return 20
        return 3

    async def dummy_fetch(query):
        return [
            {"name": "A", "c": 5},
            {"name": "B", "c": 4},
            {"name": "C", "c": 3},
        ]

    monkeypatch.setattr(report.db, "fetchval", dummy_fetchval)
    monkeypatch.setattr(report.db, "fetch", dummy_fetch)
    msg = make_msg()
    await report.report_cmd(msg)
    assert msg.answers and "Всего гостей: 10" in msg.answers[0]
