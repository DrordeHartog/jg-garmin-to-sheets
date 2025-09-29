"""
Database package for swimming analyzer.

This package handles all database operations including:
- Connection management
- Schema definitions
- CRUD operations
- Migrations
"""

from .database_manager import DatabaseManager
from .schema import create_tables, drop_tables

__all__ = [
    'DatabaseManager',
    'create_tables',
    'drop_tables'
]
