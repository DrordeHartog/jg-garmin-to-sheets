"""
Tests for the DataProcessor orchestrator and table processors.
"""

import pytest
import tempfile
import os
from datetime import date
from unittest.mock import Mock, AsyncMock

from src.orchestration.data_processor import DataProcessor
from src.orchestration.processors.base_processor import BaseTableProcessor
from src.database.database_manager import DatabaseManager


class TestDataProcessor:
    """Test the main DataProcessor orchestrator."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def db_manager(self, temp_db):
        """Create a database manager with temporary database."""
        return DatabaseManager(temp_db)
    
    @pytest.fixture
    def data_processor(self, db_manager):
        """Create a DataProcessor instance."""
        return DataProcessor(db_manager)
    
    @pytest.fixture
    def sample_raw_data(self):
        """Sample raw API data for testing."""
        return {
            'hrv_data': {'hrvSummary': {'lastNightAvg': 45}},
            'activities': [{'activityType': 'running', 'distance': 5000}],
            'sleep_data': {'sleepScore': 85},
            'stats_data': {'totalSteps': 10000},
            'summary_data': {'weight': 70.5},
            'training_status': {'vo2max_running': 50}
        }
    
    @pytest.mark.asyncio
    async def test_process_daily_data_structure(self, data_processor, sample_raw_data):
        """Test that process_daily_data returns expected structure."""
        target_date = date(2024, 9, 8)
        
        results = await data_processor.process_daily_data(sample_raw_data, target_date)
        
        # Check main structure
        assert 'target_date' in results
        assert 'processing_start' in results
        assert 'tables' in results
        assert 'summary' in results
        
        # Check all tables are processed
        expected_tables = [
            'daily_summary', 'recovery', 'activities', 'swimming_sessions',
            'swimming_intervals', 'swimming_laps', 'swimming_lengths'
        ]
        assert set(results['tables'].keys()) == set(expected_tables)
        
        # Check each table has expected structure
        for table_name in expected_tables:
            table_result = results['tables'][table_name]
            assert 'status' in table_result
            assert 'records_processed' in table_result
            assert 'runtime_seconds' in table_result
            assert 'error' in table_result
        
        # Check summary structure
        summary = results['summary']
        assert 'total_runtime_seconds' in summary
        assert 'successful_tables' in summary
        assert 'failed_tables' in summary
        assert 'total_records_processed' in summary
        assert 'processing_end' in summary
    
    @pytest.mark.asyncio
    async def test_process_daily_data_all_tables_succeed_with_zero_records(self, data_processor, sample_raw_data):
        """Test that all tables succeed but process zero records (since they're stubs)."""
        target_date = date(2024, 9, 8)
        
        results = await data_processor.process_daily_data(sample_raw_data, target_date)
        
        # All tables should succeed but process 0 records since they're stubs
        for table_name, table_result in results['tables'].items():
            assert table_result['status'] == 'SUCCESS'
            assert table_result['records_processed'] == 0
            assert table_result['error'] is None
        
        # Summary should reflect all successes but zero records
        assert results['summary']['successful_tables'] == 7
        assert results['summary']['failed_tables'] == 0
        assert results['summary']['total_records_processed'] == 0


class TestBaseTableProcessor:
    """Test the base table processor class."""
    
    def test_base_processor_abstract_methods(self):
        """Test that base processor cannot be instantiated (abstract class)."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseTableProcessor()
