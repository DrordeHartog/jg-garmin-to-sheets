"""
Base ETL Job class.

All ETL jobs inherit from this abstract base class and implement the Extract, Transform, and Load methods.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseETLJob(ABC):
    """Abstract base class for all ETL jobs."""
    
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.logger = logging.getLogger(f"{__name__}.{job_name}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete ETL job.
        
        Returns:
            Dict containing job results and metadata
        """
        self.logger.info(f"Starting ETL job: {self.job_name}")
        
        try:
            # Extract
            self.logger.info("Extracting data...")
            raw_data = self.extract()
            
            # Transform
            self.logger.info("Transforming data...")
            transformed_data = self.transform(raw_data)
            
            # Load
            self.logger.info("Loading data...")
            load_result = self.load(transformed_data)
            
            result = {
                "job_name": self.job_name,
                "status": "success",
                "extracted_records": len(raw_data) if isinstance(raw_data, list) else 1,
                "transformed_records": len(transformed_data) if isinstance(transformed_data, list) else 1,
                "load_result": load_result
            }
            
            self.logger.info(f"ETL job completed successfully: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"ETL job failed: {e}")
            return {
                "job_name": self.job_name,
                "status": "failed",
                "error": str(e)
            }
    
    @abstractmethod
    def extract(self) -> Any:
        """Extract data from source."""
        pass
    
    @abstractmethod
    def transform(self, raw_data: Any) -> Any:
        """Transform extracted data."""
        pass
    
    @abstractmethod
    def load(self, transformed_data: Any) -> Dict[str, Any]:
        """Load transformed data to destination."""
        pass