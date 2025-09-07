"""
Data models for the Garmin Swimming Analyzer.

This module contains all the data structures used throughout the application.
The models are designed to be stable and independent of API changes.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List

@dataclass
class SleepMetrics:
    """Sleep-related metrics from Garmin."""
    date: date
    sleep_time_seconds: Optional[int] = None
    nap_time_seconds: Optional[int] = None
    deep_sleep_seconds: Optional[int] = None
    light_sleep_seconds: Optional[int] = None
    rem_sleep_seconds: Optional[int] = None
    awake_sleep_seconds: Optional[int] = None
    sleep_score: Optional[float] = None
    average_respiration: Optional[float] = None
    awake_count: Optional[int] = None
    avg_sleep_stress: Optional[float] = None
    avg_heart_rate: Optional[float] = None

@dataclass
class HealthMetrics:
    """Health and fitness metrics from Garmin."""
    date: date
    # Body Composition
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    
    # Activity & Fitness
    total_calories: Optional[int] = None
    active_calories: Optional[int] = None
    bmr_calories: Optional[int] = None
    total_steps: Optional[int] = None
    total_distance_meters: Optional[float] = None
    highly_active_seconds: Optional[int] = None
    active_seconds: Optional[int] = None
    sedentary_seconds: Optional[int] = None
    intensity_minutes: Optional[int] = None
    
    # Training & Performance
    vo2max_running: Optional[float] = None
    vo2max_precise: Optional[float] = None
    training_status: Optional[str] = None
    fitness_age: Optional[int] = None
    resting_heart_rate: Optional[int] = None

@dataclass
class RecoveryMetrics:
    """Recovery and HRV metrics from Garmin."""
    date: date
    # HRV
    hrv_last_night_avg: Optional[int] = None
    hrv_weekly_avg: Optional[int] = None
    hrv_last_night_5min_high: Optional[int] = None
    hrv_status: Optional[str] = None
    hrv_feedback_phrase: Optional[str] = None
    
    # Stress & Recovery
    average_stress: Optional[int] = None

@dataclass
class SwimmingMetrics:
    """Swimming-specific metrics from Garmin."""
    date: date
    # Swimming Activity Counts
    swim_activity_count: Optional[int] = None
    pool_swim_count: Optional[int] = None
    open_water_swim_count: Optional[int] = None

    # Swimming Distance & Duration
    swim_distance_meters: Optional[float] = None
    swim_duration_min: Optional[float] = None
    swim_duration_seconds: Optional[float] = None

    # Swimming Laps & Lengths
    swim_laps: Optional[int] = None  # Total laps completed
    active_lengths: Optional[int] = None  # Active swimming lengths
    pool_length_meters: Optional[float] = None  # Pool length in meters

    # Swimming Pace & Speed
    swim_average_pace_per_100m: Optional[float] = None  # Average pace per 100m in seconds
    swim_max_pace_per_100m: Optional[float] = None  # Max pace per 100m in seconds
    swim_average_speed: Optional[float] = None  # Average speed in m/s
    swim_max_speed: Optional[float] = None  # Max speed in m/s

    # Swimming Heart Rate
    swim_average_hr: Optional[float] = None  # Average heart rate during swim
    swim_max_hr: Optional[float] = None  # Max heart rate during swim

    # Swimming Strokes & Technique
    total_strokes: Optional[int] = None  # Total strokes taken
    swim_average_strokes_per_length: Optional[float] = None  # Average strokes per length
    swim_average_strokes_per_minute: Optional[float] = None  # Stroke rate (SPM)
    swim_cadence: Optional[float] = None  # Swimming cadence

    # Swimming Efficiency Metrics
    avg_swolf: Optional[float] = None  # Average SWOLF score (strokes + time per 50m)
    min_swolf: Optional[float] = None  # Best (minimum) SWOLF score
    max_swolf: Optional[float] = None  # Worst (maximum) SWOLF score

    # Swimming Zones & Intensity
    swim_zone1_time: Optional[float] = None  # Time in zone 1 (recovery)
    swim_zone2_time: Optional[float] = None  # Time in zone 2 (aerobic base)
    swim_zone3_time: Optional[float] = None  # Time in zone 3 (tempo)
    swim_zone4_time: Optional[float] = None  # Time in zone 4 (threshold)
    swim_zone5_time: Optional[float] = None  # Time in zone 5 (VO2 max)

    # Swimming Calories & Power
    swim_calories: Optional[int] = None  # Calories burned during swim
    swim_training_effect: Optional[float] = None  # Training effect score
    swim_anaerobic_training_effect: Optional[float] = None  # Anaerobic training effect

@dataclass
class DailyMetrics:
    """Combined daily metrics container."""
    date: date
    sleep: SleepMetrics
    health: HealthMetrics
    recovery: RecoveryMetrics
    swimming: SwimmingMetrics

@dataclass
class SwimmingSession:
    """Detailed swimming session data."""
    session_id: str
    start_time: datetime
    end_time: datetime
    total_distance: float
    total_duration: float
    metrics: SwimmingMetrics
    intervals: Optional[List['SwimmingInterval']] = None

@dataclass
class SwimmingInterval:
    """Data for each interval/lap in a swimming session."""
    interval_number: int
    distance: float
    duration: float
    pace_per_100m: float
    heart_rate: Optional[float] = None
    strokes: Optional[int] = None
    swolf: Optional[float] = None
