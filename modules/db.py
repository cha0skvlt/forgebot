import logging
import asyncio
from typing import Any, List, Optional

import asyncpg
from modules.env import get_env

log = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    def _check_pool(self) -> asyncpg.Pool:
        if not self.pool:
            raise RuntimeError("Database not connected")
        return self.pool

    async def connect(self) -> None:
        dsn = get_env("POSTGRES_DSN", required=True)
        for attempt in range(10):
            try:
                self.pool = await asyncpg.create_pool(dsn)
                log.info("PostgreSQL pool created")
                return
            except Exception as e:
                log.warning("DB connect failed (%s): %s", attempt + 1, e)
                await asyncio.sleep(1)
        raise RuntimeError("Could not connect to PostgreSQL")

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
            log.info("PostgreSQL pool closed")

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        pool = self._check_pool()
        return await pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        pool = self._check_pool()
        return await pool.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        pool = self._check_pool()
        return await pool.fetchval(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        pool = self._check_pool()
        return await pool.execute(query, *args)


db = Database()


async def init_guests_table() -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS guests(
            id SERIAL PRIMARY KEY,
            uuid TEXT UNIQUE NOT NULL,
            tg_id BIGINT NULL,
            name TEXT,
            phone TEXT,
            dob DATE,
            source TEXT,
            created_at TIMESTAMP DEFAULT now(),
            agreed_at TIMESTAMP
        )
        """
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS guests_uuid_idx ON guests(uuid)"
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS guests_tg_id_idx ON guests(tg_id)"
    )
    log.info("guests table ensured")


async def init_visits_table() -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS visits(
            id SERIAL PRIMARY KEY,
            guest_id INTEGER REFERENCES guests(id),
            ts TIMESTAMP DEFAULT now()
        )
        """
    )
    await db.execute(
        "CREATE INDEX IF NOT EXISTS visits_guest_id_idx ON visits(guest_id)"
    )
    log.info("visits table ensured")
