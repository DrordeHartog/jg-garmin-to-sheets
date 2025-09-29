"""
Database package for swimming analyzer.

This package handles all database operations including:
- Connection management
- Schema definitions
- CRUD operations
- Migrations
"""

from .SQLiteManager import SQLiteManager
from .schema import create_tables, drop_tables

__all__ = [
    'SQLiteManager',
    'create_tables',
    'drop_tables'
]
