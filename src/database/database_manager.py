"""
Database connection and management utilities.

Handles SQLite database connections, setup, and configuration.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default database location in project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "swimming_analyzer.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Database manager initialized with path: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_database(self) -> bool:
        """
        Create the database file if it doesn't exist.
        
        Returns:
            bool: True if database was created or already exists
        """
        try:
            with self.get_connection() as conn:
                # Test connection by creating a simple table and dropping it
                conn.execute("CREATE TABLE IF NOT EXISTS _test (id INTEGER)")
                conn.execute("DROP TABLE _test")
                conn.commit()
            
            logger.info(f"Database created/verified at: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            dict: Database information including path, size, tables
        """
        try:
            with self.get_connection() as conn:
                # Get table list
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                
                # Get database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    "path": str(self.db_path),
                    "size_bytes": db_size,
                    "size_mb": round(db_size / (1024 * 1024), 2),
                    "tables": [table[0] for table in tables],
                    "exists": self.db_path.exists()
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file. If None, uses timestamp.
            
        Returns:
            bool: True if backup was successful
        """
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.db_path.parent / f"backup_{timestamp}.db"
            
            backup_path = Path(backup_path)
            
            with self.get_connection() as conn:
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()
            
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
