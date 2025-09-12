"""
Base class for all table processors.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict

from ....database.database_manager import DatabaseManager

# Make DatabaseManager available to child classes
__all__ = ['BaseTableProcessor', 'DatabaseManager']


class BaseTableProcessor(ABC):
    """Base class for all table processors."""
    
    @abstractmethod
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> Any:
        """Extract relevant data from raw API response."""
        pass
    
    @abstractmethod
    def transform(self, data: Any, target_date: date) -> Any:
        """Transform extracted data into data model."""
        pass
    
    @abstractmethod
    async def load(self, data: Any, db_manager: DatabaseManager) -> int:
        """Load transformed data into database table."""
        pass
