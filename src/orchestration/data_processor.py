"""
Data Processing Orchestrator for Garmin Swimming Analyzer.

This module handles the ETL pipeline from raw Garmin API data to database tables.
Each table has its own processor with extract, transform, and load methods.
"""

import asyncio
import logging
import time
from datetime import date, datetime
from typing import Dict, List, Any, Optional

from ..database.database_manager import DatabaseManager
from .processors import (
    DailySummaryProcessor, RecoveryProcessor, ActivitiesProcessor,
    SwimmingSessionsProcessor, SwimmingIntervalsProcessor, 
    SwimmingLapsProcessor, SwimmingLengthsProcessor
)

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Main orchestrator for processing Garmin API data into database tables.
    
    Each table is processed independently with its own transaction.
    Processing continues even if individual tables fail.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.processors = {
            'daily_summary': DailySummaryProcessor(),
            'recovery': RecoveryProcessor(),
            'activities': ActivitiesProcessor(),
            'swimming_sessions': SwimmingSessionsProcessor(),
            'swimming_intervals': SwimmingIntervalsProcessor(),
            'swimming_laps': SwimmingLapsProcessor(),
            'swimming_lengths': SwimmingLengthsProcessor(),
        }
    
    async def process_daily_data(self, raw_data: Dict[str, Any], target_date: date) -> Dict[str, Any]:
        """
        Process all data for a single day through the ETL pipeline.
        
        Args:
            raw_data: Raw API response data
            target_date: Date being processed
            
        Returns:
            Processing results with success/failure status for each table
        """
        start_time = time.time()
        results = {
            'target_date': target_date.isoformat(),
            'processing_start': datetime.now().isoformat(),
            'tables': {},
            'summary': {}
        }
        
        logger.info(f"Starting data processing for {target_date}")
        
        # Process each table independently
        for table_name, processor in self.processors.items():
            table_start_time = time.time()
            
            try:
                # Extract data for this table
                extracted_data = processor.extract(raw_data, target_date)
                
                # Transform data to model
                transformed_data = processor.transform(extracted_data, target_date)
                
                # Load data to database
                record_count = await processor.load(transformed_data, self.db_manager)
                
                table_runtime = time.time() - table_start_time
                
                results['tables'][table_name] = {
                    'status': 'SUCCESS',
                    'records_processed': record_count,
                    'runtime_seconds': round(table_runtime, 3),
                    'error': None
                }
                
                logger.info(f"✅ {table_name}: {record_count} records in {table_runtime:.3f}s")
                
            except Exception as e:
                table_runtime = time.time() - table_start_time
                
                results['tables'][table_name] = {
                    'status': 'FAILED',
                    'records_processed': 0,
                    'runtime_seconds': round(table_runtime, 3),
                    'error': str(e)
                }
                
                logger.error(f"❌ {table_name}: FAILED - {e}")
        
        # Calculate summary metrics
        total_runtime = time.time() - start_time
        successful_tables = sum(1 for t in results['tables'].values() if t['status'] == 'SUCCESS')
        total_records = sum(t['records_processed'] for t in results['tables'].values())
        
        results['summary'] = {
            'total_runtime_seconds': round(total_runtime, 3),
            'successful_tables': successful_tables,
            'failed_tables': len(self.processors) - successful_tables,
            'total_records_processed': total_records,
            'processing_end': datetime.now().isoformat()
        }
        
        logger.info(f"Processing complete: {successful_tables}/{len(self.processors)} tables successful, "
                   f"{total_records} total records in {total_runtime:.3f}s")
        
        return results
