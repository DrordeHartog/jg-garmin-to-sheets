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
    resting_heart_rate: Optional[int] = None
    
    # Key Sleep Metrics (for recovery analysis)
    sleep_score: Optional[float] = None
    sleep_time_seconds: Optional[int] = None

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
class SwimmingLength:
    """Individual pool length data (most granular level)."""
    length_index: int
    start_time: Optional[datetime] = None
    distance: Optional[float] = None  # Usually 25m, 33.33m, or 50m
    duration: Optional[float] = None  # Time for this length in seconds
    average_speed: Optional[float] = None  # Speed in m/s
    max_speed: Optional[float] = None
    average_hr: Optional[float] = None
    max_hr: Optional[float] = None
    total_strokes: Optional[int] = None
    swim_stroke: Optional[str] = None  # FREESTYLE, BREASTSTROKE, etc.

@dataclass
class SwimmingLap:
    """Lap data (grouped lengths within an interval)."""
    lap_id: str  # Composite key: session_id_lap_index
    interval_id: Optional[int] = None  # Will be set during load phase
    lap_index: Optional[int] = None
    start_time: Optional[datetime] = None
    distance: Optional[float] = None
    duration: Optional[float] = None  # Raw duration from API
    duration_seconds: Optional[float] = None  # Converted duration in seconds
    moving_duration: Optional[float] = None  # Raw moving duration
    moving_duration_seconds: Optional[float] = None  # Converted moving duration
    elapsed_duration: Optional[float] = None  # Raw elapsed duration
    elapsed_duration_seconds: Optional[float] = None  # Converted elapsed duration
    average_speed: Optional[float] = None
    average_moving_speed: Optional[float] = None
    max_speed: Optional[float] = None
    calories: Optional[float] = None
    bmr_calories: Optional[float] = None
    average_hr: Optional[float] = None
    max_hr: Optional[float] = None
    average_swim_cadence: Optional[float] = None
    number_of_active_lengths: Optional[int] = None
    total_strokes: Optional[int] = None
    average_strokes: Optional[float] = None
    average_swolf: Optional[float] = None
    average_stroke_distance: Optional[float] = None
    swim_drill: Optional[str] = None  # DRILL, KICK, etc.
    lengths: Optional[List[SwimmingLength]] = None

@dataclass
class SwimmingInterval:
    """Training interval data (WARMUP, ACTIVE, REST, COOLDOWN)."""
    interval_id: str  # Composite key: session_id_interval_index
    session_id: str
    interval_type: Optional[str] = None  # INTERVAL_WARMUP, INTERVAL_ACTIVE, INTERVAL_REST, INTERVAL_COOLDOWN
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    distance: Optional[float] = None
    duration: Optional[float] = None  # Raw duration from API
    duration_seconds: Optional[float] = None  # Converted duration in seconds for database
    moving_duration: Optional[float] = None
    moving_duration_seconds: Optional[float] = None  # Converted moving duration in seconds
    elapsed_duration: Optional[float] = None
    elapsed_duration_seconds: Optional[float] = None  # Converted elapsed duration in seconds
    average_speed: Optional[float] = None
    calories: Optional[float] = None
    bmr_calories: Optional[float] = None
    average_hr: Optional[float] = None
    max_hr: Optional[float] = None
    total_exercise_reps: Optional[int] = None
    message_index: Optional[int] = None
    lap_indexes: Optional[List[int]] = None
    laps: Optional[List[SwimmingLap]] = None

@dataclass
class SwimmingSession:
    """Complete swimming session data with full hierarchy and flat database fields."""
    session_id: str
    activity_id: Optional[int] = None
    date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_distance_meters: Optional[float] = None
    total_duration_seconds: Optional[int] = None
    pool_length_meters: Optional[float] = None
    
    # Summary metrics (flat fields for database)
    swim_activity_count: Optional[int] = None
    pool_swim_count: Optional[int] = None
    open_water_swim_count: Optional[int] = None
    swim_laps: Optional[int] = None
    active_lengths: Optional[int] = None
    
    # Pace and speed metrics
    swim_average_pace_per_100m: Optional[float] = None
    swim_max_pace_per_100m: Optional[float] = None
    swim_average_speed: Optional[float] = None
    swim_max_speed: Optional[float] = None
    
    # Heart rate metrics
    swim_average_hr: Optional[float] = None
    swim_max_hr: Optional[float] = None
    
    # Stroke metrics
    total_strokes: Optional[int] = None
    swim_average_strokes_per_length: Optional[float] = None
    swim_average_strokes_per_minute: Optional[float] = None
    swim_cadence: Optional[float] = None
    
    # SWOLF metrics
    avg_swolf: Optional[float] = None
    min_swolf: Optional[float] = None
    max_swolf: Optional[float] = None
    
    # Training zones
    swim_zone1_time: Optional[float] = None
    swim_zone2_time: Optional[float] = None
    swim_zone3_time: Optional[float] = None
    swim_zone4_time: Optional[float] = None
    swim_zone5_time: Optional[float] = None
    
    # Calories and training effect
    swim_calories: Optional[int] = None
    swim_training_effect: Optional[float] = None
    swim_anaerobic_training_effect: Optional[float] = None
    
    # Hierarchy data (optional, for full object model)
    summary_metrics: Optional[SwimmingMetrics] = None
    intervals: Optional[List[SwimmingInterval]] = None
    raw_splits_data: Optional[dict] = None
    raw_split_summaries: Optional[dict] = None
    raw_typed_splits: Optional[dict] = None
