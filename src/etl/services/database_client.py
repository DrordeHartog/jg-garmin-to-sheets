"""
Database Client service.

Provides database connections for ETL jobs with consistent service interface.
"""

from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Database connection service for ETL jobs."""
    
    def __init__(self, db_manager):
        """
        Initialize database client.
        
        Args:
            db_manager: DatabaseManager instance to wrap
        """
        self.db_manager = db_manager
        logger.info(f"DatabaseClient initialized with path: {self.db_manager.db_path}")
    
    def get_connection(self):
        """
        Get database connection context manager.
        
        Returns:
            Context manager for database connection
        """
        return self.db_manager.get_connection()
    
    def get_db_path(self) -> Path:
        """
        Get database file path.
        
        Returns:
            Path to database file
        """
        return self.db_manager.db_path
    
    def get_database_info(self) -> dict:
        """
        Get database information.
        
        Returns:
            Dictionary with database metadata
        """
        return self.db_manager.get_database_info()
