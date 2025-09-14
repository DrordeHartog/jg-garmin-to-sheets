"""
Test SwimmingIntervalsProcessor transform method.
"""

import pytest
import logging
from datetime import date, datetime
from pathlib import Path
import json

from src.etl.processing.processors.swimming_intervals_processor import SwimmingIntervalsProcessor
from src.shared.models import SwimmingInterval

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSwimmingIntervalsTransform:
    """Test SwimmingIntervalsProcessor transform method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = SwimmingIntervalsProcessor()
        self.test_date = date(2025, 9, 12)
        
        # Load cached data
        cache_dir = Path("data/cache")
        cache_file = cache_dir / f"{self.test_date}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.cached_data = json.load(f)
            logger.info(f"Loaded cached data from {cache_file}")
        else:
            pytest.skip(f"No cached data found for {self.test_date}")
    
    def test_transform_with_real_data(self):
        """Test transform method with real cached data."""
        # Extract data first
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        logger.info(f"Extracted {len(extracted_data)} intervals")
        
        # Transform data
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        logger.info(f"Transformed {len(transformed_data)} intervals")
        
        # Verify we have transformed data
        assert len(transformed_data) > 0, "Should have transformed intervals"
        assert all(isinstance(interval, SwimmingInterval) for interval in transformed_data)
        
        # Check first interval
        first_interval = transformed_data[0]
        logger.info(f"First interval: {first_interval}")
        
        # Verify required fields
        assert first_interval.interval_id is not None
        assert first_interval.session_id is not None
        
        # Log some key metrics
        logger.info(f"Interval types found: {set(interval.interval_type for interval in transformed_data if interval.interval_type)}")
        logger.info(f"Average duration: {sum(interval.duration for interval in transformed_data if interval.duration) / len([i for i in transformed_data if interval.duration]):.2f}s")
        logger.info(f"Total distance: {sum(interval.distance for interval in transformed_data if interval.distance):.2f}m")
    
    def test_transform_data_structure(self):
        """Test that transformed data has correct structure."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        first_interval = transformed_data[0]
        
        # Check all expected fields are present
        expected_fields = [
            'interval_id', 'session_id', 'interval_type', 'start_time', 'end_time',
            'duration_seconds', 'moving_duration_seconds', 'elapsed_duration_seconds',
            'distance_meters', 'average_speed', 'calories', 'bmr_calories',
            'average_hr', 'max_hr', 'total_exercise_reps', 'message_index'
        ]
        
        for field in expected_fields:
            assert hasattr(first_interval, field), f"Missing field: {field}"
    
    def test_transform_duration_conversion(self):
        """Test duration conversion from raw data."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        # Find an interval with duration data
        interval_with_duration = next(
            (interval for interval in transformed_data if interval.duration_seconds is not None),
            None
        )
        
        if interval_with_duration:
            logger.info(f"Duration conversion test - Raw: {interval_with_duration.duration}, Converted: {interval_with_duration.duration_seconds}s")
            assert isinstance(interval_with_duration.duration_seconds, (int, float))
            assert interval_with_duration.duration_seconds > 0
    
    def test_transform_interval_types(self):
        """Test that interval types are properly extracted."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        # Check interval types
        interval_types = [interval.interval_type for interval in transformed_data if interval.interval_type]
        logger.info(f"Found interval types: {set(interval_types)}")
        
        # Should have some interval types
        assert len(interval_types) > 0, "Should have at least one interval with a type"
    
    def test_transform_error_handling(self):
        """Test error handling in transform method."""
        # Test with empty data
        empty_result = self.processor.transform([], self.test_date)
        assert empty_result == []
        
        # Test with malformed data
        malformed_data = [{'invalid': 'data'}]
        result = self.processor.transform(malformed_data, self.test_date)
        # Should handle gracefully and return empty list or skip invalid records
        assert isinstance(result, list)
    
    def test_transform_empty_data(self):
        """Test transform with empty extracted data."""
        result = self.processor.transform([], self.test_date)
        assert result == []
        assert len(result) == 0


if __name__ == "__main__":
    # Run the test
    test_instance = TestSwimmingIntervalsTransform()
    test_instance.setup_method()
    
    try:
        test_instance.test_transform_with_real_data()
        print("✅ Transform test with real data passed")
        
        test_instance.test_transform_data_structure()
        print("✅ Data structure test passed")
        
        test_instance.test_transform_duration_conversion()
        print("✅ Duration conversion test passed")
        
        test_instance.test_transform_interval_types()
        print("✅ Interval types test passed")
        
        test_instance.test_transform_error_handling()
        print("✅ Error handling test passed")
        
        test_instance.test_transform_empty_data()
        print("✅ Empty data test passed")
        
        print("\n🎉 All SwimmingIntervalsProcessor transform tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
