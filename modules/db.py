import logging
import os
from typing import Any, List, Optional

import asyncpg

log = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    def _check_pool(self) -> asyncpg.Pool:
        if not self.pool:
            raise RuntimeError("Database not connected")
        return self.pool

    async def connect(self) -> None:
        dsn = os.getenv("POSTGRES_DSN")
        if not dsn:
            raise RuntimeError("POSTGRES_DSN is not set")
        self.pool = await asyncpg.create_pool(dsn)
        log.info("PostgreSQL pool created")

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
