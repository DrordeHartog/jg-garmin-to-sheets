"""
Base class for all table processors.
"""

import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict

from ....database.database_manager import DatabaseManager

# Make DatabaseManager available to child classes
__all__ = ['BaseTableProcessor', 'DatabaseManager']

logger = logging.getLogger(__name__)


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
    
    async def run(self, raw_data: Dict[str, Any], target_date: date, db_manager: DatabaseManager) -> int:
        """
        Run the complete ETL process: extract, transform, load.
        
        Args:
            raw_data: Raw API response data
            target_date: Target date for processing
            db_manager: Database manager instance
            
        Returns:
            Number of records loaded into database
            
        Raises:
            Exception: If any step in the ETL process fails
        """
        try:
            logger.info(f"Starting ETL process for {self.__class__.__name__} on {target_date}")
            
            # Extract data
            logger.debug("Extracting data...")
            extracted_data = self.extract(raw_data, target_date)
            logger.info(f"Extracted {len(extracted_data) if hasattr(extracted_data, '__len__') else 'unknown'} records")
            
            # Transform data
            logger.debug("Transforming data...")
            transformed_data = self.transform(extracted_data, target_date)
            logger.info(f"Transformed {len(transformed_data) if hasattr(transformed_data, '__len__') else 'unknown'} records")
            
            # Load data
            logger.debug("Loading data to database...")
            loaded_count = await self.load(transformed_data, db_manager)
            logger.info(f"Successfully loaded {loaded_count} records to database")
            
            return loaded_count
            
        except Exception as e:
            logger.error(f"ETL process failed for {self.__class__.__name__} on {target_date}: {str(e)}")
            raise
