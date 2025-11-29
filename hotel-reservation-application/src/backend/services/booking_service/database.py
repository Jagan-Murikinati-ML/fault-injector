import asyncpg
import os
from typing import Optional

class Database:
    """
    Database connection manager for PostgreSQL
    """
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def connect(self):
        """
        Create database connection pool
        """
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "hotel_booking_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "password"),
                min_size=5,
                max_size=20
            )
            
    async def disconnect(self):
        """
        Close database connection pool
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
            
    async def fetch(self, query: str, *args):
        """
        Fetch multiple rows
        """
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
            
    async def fetchrow(self, query: str, *args):
        """
        Fetch single row
        """
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
            
    async def execute(self, query: str, *args):
        """
        Execute query without returning results
        """
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

# Global database instance
db = Database()

