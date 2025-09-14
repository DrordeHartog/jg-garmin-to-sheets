#!/usr/bin/env python3
"""
Tests for SwimmingSessionsProcessor.
Tests extraction with real cached data.
"""

import json
import logging
import os
from datetime import date
from unittest.mock import Mock

import pytest

from src.etl.processing.processors.swimming_sessions_processor import SwimmingSessionsProcessor


class TestSwimmingSessionsProcessor:
    """Test cases for SwimmingSessionsProcessor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Set up logging for this test
        self.setup_logging()
        self.processor = SwimmingSessionsProcessor()
        self.target_date = date(2025, 9, 12)
    
    def setup_logging(self):
        """Set up logging configuration for tests."""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/swimming_sessions_test.log'),
                logging.StreamHandler()
            ]
        )
    
    def test_extract_with_real_cached_data(self):
        """Test swimming sessions extraction with real cached data."""
        # Load cached data
        cache_file = "data/cache/2025-09-12.json"
        if not os.path.exists(cache_file):
            pytest.skip(f"Cache file not found: {cache_file}")
        
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)
        
        # Test extraction
        extracted_sessions = self.processor.extract(raw_data, self.target_date)
        
        # Assertions
        assert len(extracted_sessions) > 0, "Should extract at least one swimming session"
        
        for session in extracted_sessions:
            # Validate required fields
            assert session['session_id'], "Session ID should not be empty"
            assert session['activity_id'], "Activity ID should not be empty"
            assert session['activity_name'], "Activity name should not be empty"
            assert session['activity_type'] == 'lap_swimming', "Activity type should be lap_swimming"
            
            # Validate data types
            assert isinstance(session['session_id'], str), "Session ID should be string"
            assert isinstance(session['activity_id'], int), "Activity ID should be int"
            assert isinstance(session['total_distance'], (int, float, type(None))), "Distance should be numeric or None"
            assert isinstance(session['total_duration'], (int, float, type(None))), "Duration should be numeric or None"
            
            # Validate positive values where applicable
            if session['total_distance'] is not None:
                assert session['total_distance'] >= 0, "Distance should be non-negative"
            if session['total_duration'] is not None:
                assert session['total_duration'] > 0, "Duration should be positive"
    
    def test_extract_with_no_swimming_activities(self):
        """Test extraction when no swimming activities are present."""
        raw_data = {
            'activities': [
                {
                    'activityId': 123,
                    'activityType': {'typeKey': 'running'},
                    'activityName': 'Morning Run'
                }
            ]
        }
        
        extracted_sessions = self.processor.extract(raw_data, self.target_date)
        
        assert len(extracted_sessions) == 0, "Should return empty list when no swimming activities"
    
    def test_extract_with_empty_activities(self):
        """Test extraction with empty activities list."""
        raw_data = {'activities': []}
        
        extracted_sessions = self.processor.extract(raw_data, self.target_date)
        
        assert len(extracted_sessions) == 0, "Should return empty list when no activities"
    
    def test_extract_with_missing_activity_id(self):
        """Test extraction with swimming activity missing activity ID."""
        raw_data = {
            'activities': [
                {
                    'activityType': {'typeKey': 'lap_swimming'},
                    'activityName': 'Swimming without ID'
                    # Missing activityId
                }
            ]
        }
        
        extracted_sessions = self.processor.extract(raw_data, self.target_date)
        
        assert len(extracted_sessions) == 0, "Should skip activities without valid session ID"
    
    def test_extract_data_structure(self):
        """Test that extracted data has expected structure."""
        raw_data = {
            'activities': [
                {
                    'activityId': 20362970280,
                    'activityName': 'Pool Swimming session 2',
                    'startTimeLocal': '2025-09-12 16:08:57',
                    'startTimeGMT': '2025-09-12 13:08:57',
                    'endTimeLocal': None,
                    'endTimeGMT': '2025-09-12 13:59:59',
                    'activityType': {'typeKey': 'lap_swimming'},
                    'eventType': {'typeKey': 'uncategorized'},
                    'distance': 1466.52,
                    'duration': 3054.13,
                    'elapsedDuration': 3062.99,
                    'movingDuration': 2436.53,
                    'averageSpeed': 0.786,
                    'maxSpeed': 2.48,
                    'averageHR': 131.0,
                    'maxHR': 175.0,
                    'minHR': None,
                    'calories': 487.0,
                    'poolLength': 33.33,
                    'lapCount': 15,
                    'activeLengths': 44,
                    'deviceId': 3493428143
                }
            ]
        }
        
        extracted_sessions = self.processor.extract(raw_data, self.target_date)
        
        assert len(extracted_sessions) == 1
        session = extracted_sessions[0]
        
        # Check all expected fields are present
        expected_fields = [
            'session_id', 'activity_id', 'activity_name', 'start_time_local',
            'total_distance', 'total_duration', 'pool_length', 'lap_count',
            'active_lengths', 'activity_type'
        ]
        
        for field in expected_fields:
            assert field in session, f"Field '{field}' should be present in extracted data"


if __name__ == "__main__":
    # Run tests manually
    test_instance = TestSwimmingSessionsProcessor()
    test_instance.setup_method()
    
    print("🏊‍♂️ Running SwimmingSessionsProcessor tests...")
    
    try:
        test_instance.test_extract_with_real_cached_data()
        print("✅ Real cached data test passed")
    except Exception as e:
        print(f"❌ Real cached data test failed: {e}")
    
    try:
        test_instance.test_extract_with_no_swimming_activities()
        print("✅ No swimming activities test passed")
    except Exception as e:
        print(f"❌ No swimming activities test failed: {e}")
    
    try:
        test_instance.test_extract_with_empty_activities()
        print("✅ Empty activities test passed")
    except Exception as e:
        print(f"❌ Empty activities test failed: {e}")
    
    try:
        test_instance.test_extract_with_missing_activity_id()
        print("✅ Missing activity ID test passed")
    except Exception as e:
        print(f"❌ Missing activity ID test failed: {e}")
    
    try:
        test_instance.test_extract_data_structure()
        print("✅ Data structure test passed")
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
    
    print("🎉 All tests completed!")
