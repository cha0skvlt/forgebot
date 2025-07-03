import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules.db import db, init_guests_table

DSN = 'postgresql://postgres:postgres@localhost/testdb'

@pytest.mark.asyncio
async def test_init_guests_table():
    os.environ['POSTGRES_DSN'] = DSN
    await db.connect()
    await db.execute('DROP TABLE IF EXISTS guests')
    await init_guests_table()
    exists = await db.fetchval("SELECT to_regclass('public.guests')")
    cols = await db.fetch(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name='guests'
        ORDER BY ordinal_position
        """
    )
    await db.close()
    assert exists == 'guests'
    names = [r['column_name'] for r in cols]
    assert names == [
        'id', 'uuid', 'tg_id', 'name', 'phone', 'dob', 'source', 'created_at'
    ]

