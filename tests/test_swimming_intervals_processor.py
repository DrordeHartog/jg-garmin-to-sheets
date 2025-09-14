#!/usr/bin/env python3
"""
Tests for SwimmingIntervalsProcessor.
Tests extraction with real cached data.
"""

import json
import logging
import os
from datetime import date
from unittest.mock import Mock

import pytest

from src.etl.processing.processors.swimming_intervals_processor import SwimmingIntervalsProcessor


class TestSwimmingIntervalsProcessor:
    """Test cases for SwimmingIntervalsProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        # Set up logging for this test
        self.setup_logging()
        self.processor = SwimmingIntervalsProcessor()
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
                logging.FileHandler('logs/swimming_intervals_test.log'),
                logging.StreamHandler()
            ]
        )

    def test_extract_with_real_cached_data(self):
        """Test swimming intervals extraction with real cached data."""
        # Load cached data
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_intervals = self.processor.extract(raw_data, self.target_date)

        # Should have 4 intervals: WARMUP, COOLDOWN, ACTIVE, REST
        assert len(extracted_intervals) == 4
        
        # Check first interval (WARMUP)
        warmup_interval = extracted_intervals[0]
        assert warmup_interval['interval_id'] == '20362970280_0'
        assert warmup_interval['session_id'] == '20362970280'
        assert warmup_interval['interval_index'] == 0
        assert warmup_interval['split_type'] == 'INTERVAL_WARMUP'
        assert warmup_interval['no_of_splits'] == 1
        assert abs(warmup_interval['duration'] - 435.306) < 0.001  # Allow for floating point precision
        assert warmup_interval['distance'] == 0.0
        
        # Check active interval (should have most data)
        active_interval = next(i for i in extracted_intervals if i['split_type'] == 'INTERVAL_ACTIVE')
        assert active_interval['no_of_splits'] == 8
        assert abs(active_interval['duration'] - 2422.791) < 0.001  # Allow for floating point precision
        assert active_interval['distance'] == 0.0
        
        print("✅ Real cached data test passed")

    def test_extract_no_swimming_activities(self):
        """Test extraction when no swimming activities are present."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "running"}, "activityId": 1},
                {"activityType": {"typeKey": "cycling"}, "activityId": 2}
            ]
        }
        extracted_intervals = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_intervals) == 0
        print("✅ No swimming activities test passed")

    def test_extract_empty_activities(self):
        """Test extraction with an empty activities list."""
        raw_data = {"activities": []}
        extracted_intervals = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_intervals) == 0
        print("✅ Empty activities test passed")

    def test_extract_missing_activity_id(self):
        """Test extraction with a swimming activity missing an activityId."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "lap_swimming"}, "activityName": "Invalid Swim"}
            ]
        }
        extracted_intervals = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_intervals) == 0  # Should be skipped due to missing ID
        print("✅ Missing activity ID test passed")

    def test_extract_no_detailed_data(self):
        """Test extraction when swimming activity has no detailed data."""
        raw_data = {
            "activities": [
                {
                    "activityId": 12345,
                    "activityType": {"typeKey": "lap_swimming"},
                    "activityName": "Swim without details"
                }
            ]
        }
        extracted_intervals = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_intervals) == 0  # Should be empty due to no detailed data
        print("✅ No detailed data test passed")

    def test_extract_data_structure(self):
        """Test that extracted data has expected structure."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_intervals = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_intervals) == 4
        
        interval = extracted_intervals[0]
        
        # Check all expected fields are present
        expected_fields = [
            'interval_id', 'session_id', 'interval_index', 'split_type',
            'no_of_splits', 'duration', 'distance', 'moving_duration',
            'average_speed', 'calories', 'bmr_calories', 'average_hr',
            'max_hr', 'total_exercise_reps', 'max_distance', 'max_distance_with_precision'
        ]
        
        for field in expected_fields:
            assert field in interval, f"Field '{field}' should be present in extracted data"

        assert isinstance(interval['interval_id'], str)
        assert isinstance(interval['session_id'], str)
        assert isinstance(interval['interval_index'], int)
        assert isinstance(interval['split_type'], str)
        assert isinstance(interval['no_of_splits'], int)
        assert isinstance(interval['duration'], (int, float))
        print("✅ Data structure test passed")


if __name__ == "__main__":
    print("🏊‍♂️ Running SwimmingIntervalsProcessor tests...")
    test_instance = TestSwimmingIntervalsProcessor()
    test_instance.setup_method()
    
    test_instance.test_extract_with_real_cached_data()
    test_instance.test_extract_no_swimming_activities()
    test_instance.test_extract_empty_activities()
    test_instance.test_extract_missing_activity_id()
    test_instance.test_extract_no_detailed_data()
    test_instance.test_extract_data_structure()
    
    print("🎉 All tests completed!")
