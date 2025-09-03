"""
Data models for the Garmin Swimming Analyzer.

This module contains all the data structures used throughout the application.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List

@dataclass
class SwimmingMetrics:
    """Swimming session metrics from Garmin."""
    date: date
    swim_activity_count: Optional[int] = None
    swim_distance_meters: Optional[float] = None
    swim_laps: Optional[int] = None
    swim_duration_min: Optional[float] = None
    pool_swim_count: Optional[int] = None
    open_water_swim_count: Optional[int] = None
    swim_average_pace_per_100m: Optional[float] = None
    swim_max_pace_per_100m: Optional[float] = None
    swim_average_hr: Optional[float] = None
    swim_max_hr: Optional[float] = None
    swim_average_strokes_per_length: Optional[float] = None
    swim_average_strokes_per_minute: Optional[float] = None
    avg_swolf: Optional[float] = None
    total_strokes: Optional[int] = None

@dataclass
class GarminMetrics:
    """General Garmin health metrics."""
    date: date
    sleep_score: Optional[float] = None
    sleep_length: Optional[float] = None
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    active_calories: Optional[int] = None
    resting_calories: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    average_stress: Optional[int] = None
    training_status: Optional[str] = None
    vo2max_running: Optional[float] = None
    vo2max_cycling: Optional[float] = None
    intensity_minutes: Optional[int] = None
    all_activity_count: Optional[int] = None
    running_activity_count: Optional[int] = None
    running_distance: Optional[float] = None
    cycling_activity_count: Optional[int] = None
    cycling_distance: Optional[float] = None
    strength_activity_count: Optional[int] = None
    strength_duration: Optional[float] = None
    cardio_activity_count: Optional[int] = None
    cardio_duration: Optional[float] = None
    tennis_activity_count: Optional[int] = None
    tennis_activity_duration: Optional[float] = None
    overnight_hrv: Optional[int] = None
    hrv_status: Optional[str] = None

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