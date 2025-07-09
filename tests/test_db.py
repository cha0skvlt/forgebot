import os
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from modules.db import db, init_guests_table, init_visits_table

DSN = 'postgresql://postgres:postgres@localhost/testdb'

@pytest.mark.asyncio
async def test_init_guests_table():
    os.environ['POSTGRES_DSN'] = DSN
    await db.connect()
    await db.execute('DROP TABLE IF EXISTS visits')
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
        'id', 'uuid', 'tg_id', 'name', 'phone', 'dob', 'source', 'created_at', 'agreed_at'
    ]


@pytest.mark.asyncio
async def test_init_tables_indices():
    os.environ['POSTGRES_DSN'] = DSN
    await db.connect()
    await db.execute('DROP TABLE IF EXISTS visits')
    await db.execute('DROP TABLE IF EXISTS guests')
    await init_guests_table()
    await init_visits_table()
    await init_guests_table()
    await init_visits_table()
    idx1 = await db.fetchval("SELECT to_regclass('public.guests_uuid_idx')")
    idx2 = await db.fetchval("SELECT to_regclass('public.guests_tg_id_idx')")
    idx3 = await db.fetchval("SELECT to_regclass('public.visits_guest_id_idx')")
    await db.close()
    assert idx1 == 'guests_uuid_idx'
    assert idx2 == 'guests_tg_id_idx'
    assert idx3 == 'visits_guest_id_idx'

