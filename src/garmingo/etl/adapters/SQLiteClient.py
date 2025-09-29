"""
Database Client service.

Provides database connections for ETL jobs with consistent service interface.
"""

import asyncio
from typing import Optional, List, Mapping, Any, Iterable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SQLiteClient:
    """Database connection service for ETL jobs."""
    
    def __init__(self, db_manager):
        """
        Initialize database client.
        
        Args:
            db_manager: SQLiteManager instance to wrap
        """
        self.db_manager = db_manager
        logger.info(f"SQLiteClient initialized with path: {self.db_manager.db_path}")
    
    async def execute_query(self, query: str, params: tuple = ()) -> Any:
        """Execute a query and return the result."""
        def _execute():
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor
        
        return await asyncio.get_event_loop().run_in_executor(None, _execute)
    
    async def execute_many(self, query: str, rows: Iterable[Any]) -> int:
        """Execute a query with multiple parameter sets."""
        def _execute_many():
            with self.db_manager.get_connection() as conn:
                cursor = conn.executemany(query, rows)
                conn.commit()
                return cursor.rowcount
        
        return await asyncio.get_event_loop().run_in_executor(None, _execute_many)
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Mapping[str, Any]]:
        """Fetch a single row from the database."""
        def _fetch_one():
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
        
        return await asyncio.get_event_loop().run_in_executor(None, _fetch_one)
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Mapping[str, Any]]:
        """Fetch all rows from the database."""
        def _fetch_all():
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        return await asyncio.get_event_loop().run_in_executor(None, _fetch_all)
