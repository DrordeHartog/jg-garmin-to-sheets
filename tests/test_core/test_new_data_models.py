"""
Tests for the new data model structure.

This module tests the updated data models that separate concerns
into SleepMetrics, HealthMetrics, RecoveryMetrics, and SwimmingMetrics.
"""

import pytest
from datetime import date
from src.shared.models import (
    SleepMetrics, 
    HealthMetrics, 
    RecoveryMetrics, 
    SwimmingMetrics, 
    DailyMetrics
)


class TestNewDataModels:
    """Test the new data model structure."""
    
    def test_sleep_metrics_creation(self):
        """Test creating SleepMetrics instance."""
        sleep = SleepMetrics(
            date=date(2025, 9, 3),
            sleep_time_seconds=22364,
            deep_sleep_seconds=2700,
            light_sleep_seconds=17100,
            rem_sleep_seconds=2580,
            awake_sleep_seconds=2400,
            sleep_score=85.0,
            average_respiration=15.0,
            awake_count=2,
            avg_sleep_stress=21.0,
            avg_heart_rate=69.0
        )
        
        assert sleep.date == date(2025, 9, 3)
        assert sleep.sleep_time_seconds == 22364
        assert sleep.deep_sleep_seconds == 2700
        assert sleep.sleep_score == 85.0
        assert sleep.avg_heart_rate == 69.0
    
    def test_health_metrics_creation(self):
        """Test creating HealthMetrics instance."""
        health = HealthMetrics(
            date=date(2025, 9, 3),
            weight=75.5,
            body_fat=15.2,
            total_calories=2788,
            active_calories=614,
            bmr_calories=2174,
            total_steps=5768,
            total_distance_meters=5614.0,
            highly_active_seconds=83,
            active_seconds=6007,
            sedentary_seconds=50598,
            vo2max_running=43.0,
            vo2max_precise=42.9,
            training_status="RECOVERY",
            resting_heart_rate=55
        )
        
        assert health.date == date(2025, 9, 3)
        assert health.weight == 75.5
        assert health.total_calories == 2788
        assert health.vo2max_running == 43.0
        assert health.training_status == "RECOVERY"
    
    def test_recovery_metrics_creation(self):
        """Test creating RecoveryMetrics instance."""
        recovery = RecoveryMetrics(
            date=date(2025, 9, 3),
            hrv_last_night_avg=33,
            hrv_weekly_avg=33,
            hrv_last_night_5min_high=46,
            hrv_status="LOW",
            hrv_feedback_phrase="HRV_LOW_1",
            average_stress=25
        )
        
        assert recovery.date == date(2025, 9, 3)
        assert recovery.hrv_last_night_avg == 33
        assert recovery.hrv_status == "LOW"
        assert recovery.average_stress == 25
    
    def test_swimming_metrics_creation(self):
        """Test creating SwimmingMetrics instance with all discovered fields."""
        swimming = SwimmingMetrics(
            date=date(2025, 9, 3),
            swim_activity_count=1,
            pool_swim_count=1,
            open_water_swim_count=0,
            swim_distance_meters=800.0,
            swim_duration_seconds=1800.0,
            swim_laps=16,
            active_lengths=24,
            pool_length_meters=33.33,
            swim_average_speed=0.44,
            swim_max_speed=0.55,
            swim_average_hr=145.0,
            swim_max_hr=165.0,
            total_strokes=320,
            swim_average_strokes_per_length=13.3,
            swim_average_strokes_per_minute=19.0,
            swim_cadence=19.0,
            avg_swolf=71.0,
            min_swolf=65.0,
            max_swolf=78.0,
            swim_zone1_time=300.0,
            swim_zone2_time=900.0,
            swim_zone3_time=600.0,
            swim_zone4_time=0.0,
            swim_zone5_time=0.0,
            swim_calories=450,
            swim_training_effect=3.2,
            swim_anaerobic_training_effect=1.8
        )
        
        assert swimming.date == date(2025, 9, 3)
        assert swimming.swim_laps == 16
        assert swimming.active_lengths == 24
        assert swimming.pool_length_meters == 33.33
        assert swimming.avg_swolf == 71.0
        assert swimming.swim_training_effect == 3.2
    
    def test_daily_metrics_container(self):
        """Test creating DailyMetrics container with all sub-metrics."""
        sleep = SleepMetrics(date=date(2025, 9, 3), sleep_time_seconds=22364)
        health = HealthMetrics(date=date(2025, 9, 3), total_calories=2788)
        recovery = RecoveryMetrics(date=date(2025, 9, 3), hrv_last_night_avg=33)
        swimming = SwimmingMetrics(date=date(2025, 9, 3), swim_laps=16)
        
        daily = DailyMetrics(
            date=date(2025, 9, 3),
            sleep=sleep,
            health=health,
            recovery=recovery,
            swimming=swimming
        )
        
        assert daily.date == date(2025, 9, 3)
        assert daily.sleep.sleep_time_seconds == 22364
        assert daily.health.total_calories == 2788
        assert daily.recovery.hrv_last_night_avg == 33
        assert daily.swimming.swim_laps == 16
    
    def test_optional_fields_handling(self):
        """Test that optional fields can be None."""
        sleep = SleepMetrics(date=date(2025, 9, 3))
        health = HealthMetrics(date=date(2025, 9, 3))
        recovery = RecoveryMetrics(date=date(2025, 9, 3))
        swimming = SwimmingMetrics(date=date(2025, 9, 3))
        
        # All optional fields should be None by default
        assert sleep.sleep_time_seconds is None
        assert health.total_calories is None
        assert recovery.hrv_last_night_avg is None
        assert swimming.swim_laps is None
    
    def test_data_model_stability(self):
        """Test that data model field names are stable (independent of API changes)."""
        # This test ensures our data model field names don't change
        # even if the Garmin API field names change
        
        swimming = SwimmingMetrics(date=date(2025, 9, 3))
        
        # These field names should remain stable
        expected_fields = [
            'swim_laps',           # Maps to API 'lapCount'
            'active_lengths',      # Maps to API 'activeLengths'
            'pool_length_meters',  # Maps to API 'poolLength' (with correction)
            'avg_swolf',          # Maps to API 'averageSwolf'
            'swim_training_effect' # Maps to API 'trainingEffect'
        ]
        
        for field in expected_fields:
            assert hasattr(swimming, field), f"Field {field} should exist in SwimmingMetrics"
