import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules import qr


def test_make_qr_link(monkeypatch):
    def dummy_make(data):
        assert data == "t.me/bot?start=uuid"
        class Img:
            def save(self, buf, format="PNG"):
                buf.write(b"img")
        return Img()
    monkeypatch.setattr(qr.qrcode, "make", dummy_make)
    url, data = qr.make_qr_link("uuid", "bot")
    assert url == "t.me/bot?start=uuid"
    assert data == b"img"

