#!/usr/bin/env python3
"""
Tests for SwimmingLengthsProcessor.
Tests extraction with real cached data.
"""

import json
import logging
import os
from datetime import date
from unittest.mock import Mock

import pytest

from src.etl.processing.processors.swimming_lengths_processor import SwimmingLengthsProcessor


class TestSwimmingLengthsProcessor:
    """Test cases for SwimmingLengthsProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        # Set up logging for this test
        self.setup_logging()
        self.processor = SwimmingLengthsProcessor()
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
                logging.FileHandler('logs/swimming_lengths_test.log'),
                logging.StreamHandler()
            ]
        )

    def test_extract_with_real_cached_data(self):
        """Test swimming lengths extraction with real cached data."""
        # Load cached data
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_lengths = self.processor.extract(raw_data, self.target_date)

        # Should have many lengths (each lap has multiple lengths)
        assert len(extracted_lengths) > 0
        
        # Check first length
        first_length = extracted_lengths[0]
        assert first_length['length_id'] == '20362970280_1_1'
        assert first_length['lap_id'] == '20362970280_1'
        assert first_length['session_id'] == '20362970280'
        assert first_length['lap_index'] == 1
        assert first_length['length_index'] == 1
        assert first_length['distance'] == 33.33
        assert first_length['duration'] == 50.0
        assert first_length['swim_stroke'] == 'BREASTSTROKE'
        assert first_length['total_strokes'] == 17
        assert first_length['average_swolf'] == 67.0
        
        # Check that we have stroke data
        strokes = [length['swim_stroke'] for length in extracted_lengths if length['swim_stroke'] is not None]
        assert len(strokes) > 0, "Should have stroke data for lengths"
        
        # Check that we have distance data (33.33m per length)
        distances = [length['distance'] for length in extracted_lengths if length['distance'] is not None]
        assert len(distances) > 0, "Should have distance data for lengths"
        assert all(d == 33.33 for d in distances), "All lengths should be 33.33m (pool length)"
        
        print("✅ Real cached data test passed")

    def test_extract_no_swimming_activities(self):
        """Test extraction when no swimming activities are present."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "running"}, "activityId": 1},
                {"activityType": {"typeKey": "cycling"}, "activityId": 2}
            ]
        }
        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_lengths) == 0
        print("✅ No swimming activities test passed")

    def test_extract_empty_activities(self):
        """Test extraction with an empty activities list."""
        raw_data = {"activities": []}
        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_lengths) == 0
        print("✅ Empty activities test passed")

    def test_extract_missing_activity_id(self):
        """Test extraction with a swimming activity missing an activityId."""
        raw_data = {
            "activities": [
                {"activityType": {"typeKey": "lap_swimming"}, "activityName": "Invalid Swim"}
            ]
        }
        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_lengths) == 0  # Should be skipped due to missing ID
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
        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_lengths) == 0  # Should be empty due to no detailed data
        print("✅ No detailed data test passed")

    def test_extract_data_structure(self):
        """Test that extracted data has expected structure."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        assert len(extracted_lengths) > 0
        
        length = extracted_lengths[0]
        
        # Check all expected fields are present
        expected_fields = [
            'length_id', 'lap_id', 'session_id', 'lap_index', 'length_index',
            'start_time_gmt', 'distance', 'duration', 'average_speed', 'max_speed',
            'average_hr', 'max_hr', 'total_strokes', 'swim_stroke', 'average_swolf'
        ]
        
        for field in expected_fields:
            assert field in length, f"Field '{field}' should be present in extracted data"

        assert isinstance(length['length_id'], str)
        assert isinstance(length['lap_id'], str)
        assert isinstance(length['session_id'], str)
        assert isinstance(length['lap_index'], int)
        assert isinstance(length['length_index'], int)
        assert isinstance(length['distance'], (int, float))
        assert isinstance(length['duration'], (int, float))
        print("✅ Data structure test passed")

    def test_length_distance_validation(self):
        """Test that length distances are correct (33.33m pool length)."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        
        # Check that we have distance data
        distances = [length['distance'] for length in extracted_lengths if length['distance'] is not None]
        assert len(distances) > 0, "Should have distance data"
        
        # Check that all lengths are 33.33m (pool length)
        for distance in distances:
            assert distance == 33.33, f"Length distance {distance} should be 33.33m (pool length)"
        
        print("✅ Length distance validation test passed")

    def test_stroke_analysis(self):
        """Test that we can analyze different swim strokes."""
        cache_file = "data/cache/2025-09-12.json"
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)

        extracted_lengths = self.processor.extract(raw_data, self.target_date)
        
        # Check that we have stroke data
        strokes = [length['swim_stroke'] for length in extracted_lengths if length['swim_stroke'] is not None]
        assert len(strokes) > 0, "Should have stroke data"
        
        # Check for different stroke types
        unique_strokes = set(strokes)
        assert len(unique_strokes) > 0, "Should have different stroke types"
        
        # Common stroke types
        expected_strokes = {'BREASTSTROKE', 'FREESTYLE', 'BACKSTROKE', 'BUTTERFLY'}
        found_strokes = unique_strokes.intersection(expected_strokes)
        assert len(found_strokes) > 0, f"Should have common stroke types, found: {unique_strokes}"
        
        print("✅ Stroke analysis test passed")


if __name__ == "__main__":
    print("🏊‍♂️ Running SwimmingLengthsProcessor tests...")
    test_instance = TestSwimmingLengthsProcessor()
    test_instance.setup_method()
    
    test_instance.test_extract_with_real_cached_data()
    test_instance.test_extract_no_swimming_activities()
    test_instance.test_extract_empty_activities()
    test_instance.test_extract_missing_activity_id()
    test_instance.test_extract_no_detailed_data()
    test_instance.test_extract_data_structure()
    test_instance.test_length_distance_validation()
    test_instance.test_stroke_analysis()
    
    print("🎉 All tests completed!")
