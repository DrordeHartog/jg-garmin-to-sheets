#!/usr/bin/env python3
"""
Tests for SwimmingLapsProcessor.
Tests extraction with real cached data.
"""

import json
import logging
import os
from datetime import date
from unittest.mock import Mock

import pytest

from src.etl.processing.processors.swimming_laps_processor import SwimmingLapsProcessor


class TestSwimmingLapsProcessor:
    """Test cases for SwimmingLapsProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        # Set up logging for this test
        self.setup_logging()
        self.processor = SwimmingLapsProcessor()
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
                logging.FileHandler('logs/swimming_laps_test.log'),
                logging.StreamHandler()
            ]
        )

    def test_extract_with_real_cached_data(self):
        """Test swimming laps extraction with real cached data."""
        # Load cached data
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_laps = self.processor.extract(raw_data, self.target_date)

        # Should have 15 laps based on our earlier investigation
        assert len(extracted_laps) == 15
        
        # Check first lap
        first_lap = extracted_laps[0]
        assert first_lap['lap_id'] == '20362970280_1'
        assert first_lap['session_id'] == '20362970280'
        assert first_lap['lap_index'] == 1
        assert first_lap['wkt_step_index'] == 0
        assert first_lap['distance'] == 299.97
        assert first_lap['duration'] == 435.337
        assert first_lap['calories'] == 71.0
        assert first_lap['average_hr'] == 135.0
        assert first_lap['total_strokes'] == 118
        assert first_lap['average_swolf'] == 60.0
        
        # Check that we have distance data (unlike intervals)
        distances = [lap['distance'] for lap in extracted_laps if lap['distance'] is not None]
        assert len(distances) > 0, "Should have distance data for laps"
        assert all(d >= 0 for d in distances), "Lap distances should be non-negative (0 for rest/drills)"
        
        print("✅ Real cached data test passed")

    def test_extract_no_swimming_activities(self):
        """Test extraction when no swimming activities are present."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "running"}, "activityId": 1},
                {"activityType": {"typeKey": "cycling"}, "activityId": 2}
            ]
        }
        extracted_laps = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_laps) == 0
        print("✅ No swimming activities test passed")

    def test_extract_empty_activities(self):
        """Test extraction with an empty activities list."""
        raw_data = {"activities": []}
        extracted_laps = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_laps) == 0
        print("✅ Empty activities test passed")

    def test_extract_missing_activity_id(self):
        """Test extraction with a swimming activity missing an activityId."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "lap_swimming"}, "activityName": "Invalid Swim"}
            ]
        }
        extracted_laps = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_laps) == 0  # Should be skipped due to missing ID
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
        extracted_laps = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_laps) == 0  # Should be empty due to no detailed data
        print("✅ No detailed data test passed")

    def test_extract_data_structure(self):
        """Test that extracted data has expected structure."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_laps = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_laps) == 15
        
        lap = extracted_laps[0]
        
        # Check all expected fields are present
        expected_fields = [
            'lap_id', 'session_id', 'lap_index', 'wkt_step_index', 'start_time_gmt',
            'distance', 'duration', 'moving_duration', 'elapsed_duration',
            'average_speed', 'average_moving_speed', 'max_speed', 'calories',
            'bmr_calories', 'average_hr', 'max_hr', 'average_swim_cadence',
            'number_of_active_lengths', 'total_strokes', 'average_strokes',
            'average_swolf', 'average_stroke_distance', 'swim_drill'
        ]
        
        for field in expected_fields:
            assert field in lap, f"Field '{field}' should be present in extracted data"

        assert isinstance(lap['lap_id'], str)
        assert isinstance(lap['session_id'], str)
        assert isinstance(lap['lap_index'], int)
        assert isinstance(lap['distance'], (int, float))
        assert isinstance(lap['duration'], (int, float))
        print("✅ Data structure test passed")

    def test_lap_distance_validation(self):
        """Test that lap distances are reasonable and match expected patterns."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_laps = self.processor.extract(raw_data, self.target_date)
        
        # Check that we have distance data
        distances = [lap['distance'] for lap in extracted_laps if lap['distance'] is not None]
        assert len(distances) > 0, "Should have distance data"
        
        # Check that distances are reasonable (pool length is ~33.33m, so laps should be ~300m or 0 for rest/drills)
        for distance in distances:
            assert 0 <= distance <= 400, f"Lap distance {distance} should be reasonable for pool swimming (0 for rest/drills)"
        
        # Check that total distance matches session total (1466.52m)
        total_lap_distance = sum(distances)
        expected_total = 1466.52
        assert abs(total_lap_distance - expected_total) < 1.0, f"Total lap distance {total_lap_distance} should match session total {expected_total}"
        
        print("✅ Lap distance validation test passed")


if __name__ == "__main__":
    print("🏊‍♂️ Running SwimmingLapsProcessor tests...")
    test_instance = TestSwimmingLapsProcessor()
    test_instance.setup_method()
    
    test_instance.test_extract_with_real_cached_data()
    test_instance.test_extract_no_swimming_activities()
    test_instance.test_extract_empty_activities()
    test_instance.test_extract_missing_activity_id()
    test_instance.test_extract_no_detailed_data()
    test_instance.test_extract_data_structure()
    test_instance.test_lap_distance_validation()
    
    print("🎉 All tests completed!")
