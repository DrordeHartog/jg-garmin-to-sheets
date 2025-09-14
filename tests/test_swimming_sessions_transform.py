#!/usr/bin/env python3
"""
Tests for SwimmingSessionsProcessor transform method.
Tests the refactored transform with shared utilities.
"""

import json
import logging
import os
from datetime import date, datetime
from unittest.mock import Mock

import pytest

from src.etl.processing.processors.swimming_sessions_processor import SwimmingSessionsProcessor


class TestSwimmingSessionsTransform:
    """Test cases for SwimmingSessionsProcessor transform method."""

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
                logging.FileHandler('logs/swimming_sessions_transform_test.log'),
                logging.StreamHandler()
            ]
        )

    def test_transform_with_real_cached_data(self):
        """Test transform method with real cached data."""
        # Load cached data
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        # First extract the data
        extracted_data = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_data) > 0, "Should have extracted session data"
        
        # Now transform the extracted data
        transformed_sessions = self.processor.transform(extracted_data, self.target_date)
        
        # Should have transformed sessions
        assert len(transformed_sessions) > 0, "Should have transformed sessions"
        assert len(transformed_sessions) == len(extracted_data), "Should transform all extracted sessions"
        
        # Check first transformed session
        first_session = transformed_sessions[0]
        assert first_session.session_id == "20362970280"
        assert first_session.activity_id == 20362970280
        assert first_session.date == self.target_date
        assert first_session.start_time is not None
        assert first_session.end_time is not None
        assert abs(first_session.total_distance_meters - 1466.52) < 0.1  # Allow for floating point precision
        assert first_session.total_duration_seconds == 3054  # Converted from 3054.1259765625
        # Pool length is in the data as 3333.0 (likely centimeters), so 33.33 meters
        assert abs(first_session.pool_length_meters - 3333.0) < 0.1  # Allow for floating point precision
        assert first_session.swim_activity_count == 1
        assert first_session.pool_swim_count == 1
        assert first_session.open_water_swim_count == 0
        assert first_session.swim_laps == 15
        assert first_session.active_lengths == 44
        assert first_session.swim_average_hr == 131.0
        assert first_session.swim_max_hr == 175.0
        assert first_session.total_strokes is None  # Not in the extracted data
        assert first_session.swim_calories == 487
        
        # Check calculated metrics
        assert first_session.swim_average_pace_per_100m is not None, "Should calculate pace per 100m"
        assert first_session.swim_average_pace_per_100m > 0, "Pace should be positive"
        
        print("✅ Real cached data transform test passed")

    def test_transform_datetime_parsing(self):
        """Test datetime parsing in transform method."""
        extracted_data = [{
            'session_id': 'test_123',
            'activity_id': 123,
            'start_time_gmt': '2025-09-12T13:08:57.0',
            'end_time_gmt': '2025-09-12T14:00:00.0',
            'total_distance': 1000.0,
            'total_duration': 3600.0,
            'pool_length': 25.0,
            'lap_count': 40,
            'active_lengths': 40,
            'average_hr': 150.0,
            'max_hr': 180.0,
            'total_strokes': 800,
            'calories': 500
        }]
        
        transformed_sessions = self.processor.transform(extracted_data, self.target_date)
        
        assert len(transformed_sessions) == 1
        session = transformed_sessions[0]
        
        # Check datetime parsing
        assert session.start_time is not None
        assert session.end_time is not None
        assert isinstance(session.start_time, datetime)
        assert isinstance(session.end_time, datetime)
        
        # Check duration conversion
        assert session.total_duration_seconds == 3600
        
        print("✅ Datetime parsing test passed")

    def test_transform_calculated_metrics(self):
        """Test calculated metrics in transform method."""
        extracted_data = [{
            'session_id': 'test_456',
            'activity_id': 456,
            'start_time_gmt': '2025-09-12T13:08:57.0',
            'end_time_gmt': '2025-09-12T14:00:00.0',
            'total_distance': 2000.0,  # 2km
            'total_duration': 3600.0,  # 1 hour
            'pool_length': 50.0,
            'lap_count': 40,
            'active_lengths': 40,
            'average_hr': 150.0,
            'max_hr': 180.0,
            'total_strokes': 1600,  # 800 strokes per km
            'calories': 500
        }]
        
        transformed_sessions = self.processor.transform(extracted_data, self.target_date)
        
        assert len(transformed_sessions) == 1
        session = transformed_sessions[0]
        
        # Check pace calculation (2km in 1 hour = 30 minutes per 100m)
        expected_pace = (3600.0 / 2000.0) * 100  # 180 seconds per 100m
        assert session.swim_average_pace_per_100m == expected_pace
        
        # Check strokes per length (1600 strokes / 40 lengths = 40 strokes per length)
        expected_strokes_per_length = 1600 / 40
        assert session.swim_average_strokes_per_length == expected_strokes_per_length
        
        # Check strokes per minute (1600 strokes / 60 minutes = 26.67 strokes per minute)
        expected_strokes_per_minute = 1600 / 60
        assert abs(session.swim_average_strokes_per_minute - expected_strokes_per_minute) < 0.01
        
        print("✅ Calculated metrics test passed")

    def test_transform_swim_type_detection(self):
        """Test pool vs open water swim type detection."""
        # Pool swim (has pool_length)
        pool_data = [{
            'session_id': 'pool_123',
            'activity_id': 123,
            'start_time_gmt': '2025-09-12T13:08:57.0',
            'end_time_gmt': '2025-09-12T14:00:00.0',
            'total_distance': 1000.0,
            'total_duration': 1800.0,
            'pool_length': 25.0,  # Has pool length = pool swim
            'lap_count': 40,
            'active_lengths': 40,
            'average_hr': 150.0,
            'max_hr': 180.0,
            'total_strokes': 800,
            'calories': 500
        }]
        
        pool_sessions = self.processor.transform(pool_data, self.target_date)
        pool_session = pool_sessions[0]
        assert pool_session.pool_swim_count == 1
        assert pool_session.open_water_swim_count == 0
        
        # Open water swim (no pool_length)
        open_water_data = [{
            'session_id': 'open_water_456',
            'activity_id': 456,
            'start_time_gmt': '2025-09-12T13:08:57.0',
            'end_time_gmt': '2025-09-12T14:00:00.0',
            'total_distance': 2000.0,
            'total_duration': 3600.0,
            # No pool_length = open water swim
            'lap_count': 0,
            'active_lengths': 0,
            'average_hr': 150.0,
            'max_hr': 180.0,
            'total_strokes': 0,
            'calories': 500
        }]
        
        open_water_sessions = self.processor.transform(open_water_data, self.target_date)
        open_water_session = open_water_sessions[0]
        assert open_water_session.pool_swim_count == 0
        assert open_water_session.open_water_swim_count == 1
        
        print("✅ Swim type detection test passed")

    def test_transform_error_handling(self):
        """Test error handling in transform method."""
        # Test with invalid data
        invalid_data = [{
            'session_id': 'invalid_123',
            'activity_id': 123,
            'start_time_gmt': 'invalid_datetime',
            'end_time_gmt': 'invalid_datetime',
            'total_distance': 'not_a_number',
            'total_duration': 'not_a_number',
            'pool_length': 25.0,
            'lap_count': 40,
            'active_lengths': 40,
            'average_hr': 150.0,
            'max_hr': 180.0,
            'total_strokes': 800,
            'calories': 500
        }]
        
        # Should not crash, should handle errors gracefully
        transformed_sessions = self.processor.transform(invalid_data, self.target_date)
        
        assert len(transformed_sessions) == 1, "Should still create session despite invalid data"
        session = transformed_sessions[0]
        assert session.session_id == 'invalid_123'
        assert session.start_time is None, "Invalid datetime should be None"
        assert session.end_time is None, "Invalid datetime should be None"
        assert session.total_duration_seconds is None, "Invalid duration should be None"
        assert session.swim_average_pace_per_100m is None, "Invalid data should result in None pace"
        
        print("✅ Error handling test passed")

    def test_transform_empty_data(self):
        """Test transform with empty data."""
        transformed_sessions = self.processor.transform([], self.target_date)
        assert len(transformed_sessions) == 0
        print("✅ Empty data test passed")


if __name__ == "__main__":
    print("🏊‍♂️ Running SwimmingSessionsProcessor transform tests...")
    test_instance = TestSwimmingSessionsTransform()
    test_instance.setup_method()
    
    test_instance.test_transform_with_real_cached_data()
    test_instance.test_transform_datetime_parsing()
    test_instance.test_transform_calculated_metrics()
    test_instance.test_transform_swim_type_detection()
    test_instance.test_transform_error_handling()
    test_instance.test_transform_empty_data()
    
    print("🎉 All transform tests completed!")
