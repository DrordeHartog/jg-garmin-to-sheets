"""
Test SwimmingLapsProcessor transform method.
"""

import pytest
import logging
from datetime import date, datetime
from pathlib import Path
import json

from src.etl.processing.processors.swimming_laps_processor import SwimmingLapsProcessor
from src.shared.models import SwimmingLap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSwimmingLapsTransform:
    """Test SwimmingLapsProcessor transform method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = SwimmingLapsProcessor()
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
        logger.info(f"Extracted {len(extracted_data)} laps")
        
        # Transform data
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        logger.info(f"Transformed {len(transformed_data)} laps")
        
        # Verify we have transformed data
        assert len(transformed_data) > 0, "Should have transformed laps"
        assert all(isinstance(lap, SwimmingLap) for lap in transformed_data)
        
        # Check first lap
        first_lap = transformed_data[0]
        logger.info(f"First lap: {first_lap}")
        
        # Verify required fields
        assert first_lap.lap_id is not None
        assert first_lap.lap_index is not None
        
        # Log some key metrics
        lap_indices = [lap.lap_index for lap in transformed_data if lap.lap_index is not None]
        durations = [lap.duration for lap in transformed_data if lap.duration is not None]
        distances = [lap.distance for lap in transformed_data if lap.distance is not None]
        
        logger.info(f"Lap indices found: {sorted(set(lap_indices))}")
        if durations:
            logger.info(f"Average duration: {sum(durations) / len(durations):.2f}s")
        if distances:
            logger.info(f"Total distance: {sum(distances):.2f}m")
    
    def test_transform_data_structure(self):
        """Test that transformed data has correct structure."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        first_lap = transformed_data[0]
        
        # Check all expected fields are present
        expected_fields = [
            'lap_id', 'interval_id', 'lap_index', 'start_time', 'distance',
            'duration', 'duration_seconds', 'moving_duration', 'moving_duration_seconds',
            'elapsed_duration', 'elapsed_duration_seconds', 'average_speed',
            'average_moving_speed', 'max_speed', 'calories', 'bmr_calories',
            'average_hr', 'max_hr', 'average_swim_cadence', 'number_of_active_lengths',
            'total_strokes', 'average_strokes', 'average_swolf', 'average_stroke_distance',
            'swim_drill'
        ]
        
        for field in expected_fields:
            assert hasattr(first_lap, field), f"Missing field: {field}"
    
    def test_transform_duration_conversion(self):
        """Test duration conversion from raw data."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        # Find a lap with duration data
        lap_with_duration = next(
            (lap for lap in transformed_data if lap.duration_seconds is not None),
            None
        )
        
        if lap_with_duration:
            logger.info(f"Duration conversion test - Raw: {lap_with_duration.duration}, Converted: {lap_with_duration.duration_seconds}s")
            assert isinstance(lap_with_duration.duration_seconds, (int, float))
            assert lap_with_duration.duration_seconds > 0
    
    def test_transform_lap_indices(self):
        """Test that lap indices are properly extracted."""
        extracted_data = self.processor.extract(self.cached_data, self.test_date)
        transformed_data = self.processor.transform(extracted_data, self.test_date)
        
        if not transformed_data:
            pytest.skip("No transformed data to test")
        
        # Check lap indices
        lap_indices = [lap.lap_index for lap in transformed_data if lap.lap_index is not None]
        logger.info(f"Found lap indices: {sorted(set(lap_indices))}")
        
        # Should have some lap indices
        assert len(lap_indices) > 0, "Should have at least one lap with an index"
    
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
    test_instance = TestSwimmingLapsTransform()
    test_instance.setup_method()
    
    try:
        test_instance.test_transform_with_real_data()
        print("✅ Transform test with real data passed")
        
        test_instance.test_transform_data_structure()
        print("✅ Data structure test passed")
        
        test_instance.test_transform_duration_conversion()
        print("✅ Duration conversion test passed")
        
        test_instance.test_transform_lap_indices()
        print("✅ Lap indices test passed")
        
        test_instance.test_transform_error_handling()
        print("✅ Error handling test passed")
        
        test_instance.test_transform_empty_data()
        print("✅ Empty data test passed")
        
        print("\n🎉 All SwimmingLapsProcessor transform tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
