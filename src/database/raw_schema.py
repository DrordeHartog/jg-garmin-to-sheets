"""
Raw database schema definitions for the swimming analyzer.

This module contains raw table creation and schema management functions.
Raw tables store data directly from the Garmin API without processing.
"""

import sqlite3
import logging
from typing import List

logger = logging.getLogger(__name__)


def create_raw_tables(conn: sqlite3.Connection) -> None:
    """
    Create all raw database tables with proper relationships and indexes.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating raw database tables...")
    
    # 1. Raw Daily Summary Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_daily_summary (
            date DATE PRIMARY KEY,
            total_calories INTEGER,
            active_calories INTEGER,
            bmr_calories INTEGER,
            total_steps INTEGER,
            total_distance_meters REAL,
            weight REAL,
            body_fat REAL,
            blood_pressure_systolic INTEGER,
            blood_pressure_diastolic INTEGER,
            vo2max_running REAL,
            vo2max_precise REAL,
            training_status TEXT,
            fitness_age INTEGER
        )
    """)
    
    # 2. Raw Recovery Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_recovery (
            date DATE PRIMARY KEY,
            -- Sleep metrics (only fields we actually extract from API)
            sleep_time_seconds INTEGER,
            sleep_score REAL,
            -- HRV metrics
            hrv_last_night_avg INTEGER,
            hrv_weekly_avg INTEGER,
            hrv_last_night_5min_high INTEGER,
            hrv_status TEXT,
            hrv_feedback_phrase TEXT,
            -- Stress & Recovery
            average_stress INTEGER,
            resting_heart_rate INTEGER
        )
    """)
    
    # 3. Raw Activities Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_activities (
            activity_id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            activity_type TEXT NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            duration_seconds INTEGER,
            distance_meters REAL,
            calories INTEGER,
            average_hr REAL,
            max_hr REAL
        )
    """)
    
    # 4. Raw Swimming Sessions Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_swimming_sessions (
            session_id TEXT PRIMARY KEY,
            activity_id INTEGER UNIQUE,
            date DATE NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            total_distance_meters REAL,
            total_duration_seconds INTEGER,
            pool_length_meters REAL,
            -- Summary metrics
            swim_activity_count INTEGER,
            pool_swim_count INTEGER,
            open_water_swim_count INTEGER,
            swim_laps INTEGER,
            active_lengths INTEGER,
            swim_average_pace_per_100m REAL,
            swim_max_pace_per_100m REAL,
            swim_average_speed REAL,
            swim_max_speed REAL,
            swim_average_hr REAL,
            swim_max_hr REAL,
            total_strokes INTEGER,
            swim_average_strokes_per_length REAL,
            swim_average_strokes_per_minute REAL,
            swim_cadence REAL,
            avg_swolf REAL,
            min_swolf REAL,
            max_swolf REAL,
            swim_zone1_time REAL,
            swim_zone2_time REAL,
            swim_zone3_time REAL,
            swim_zone4_time REAL,
            swim_zone5_time REAL,
            swim_calories INTEGER,
            swim_training_effect REAL,
            swim_anaerobic_training_effect REAL
        )
    """)
    
    
    # 6. Raw Swimming Laps Table (Updated with interval fields)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_swimming_laps (
            lap_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            lap_index INTEGER NOT NULL,
            wkt_step_index INTEGER,
            start_time DATETIME,
            distance REAL,
            duration REAL,
            duration_seconds REAL,
            moving_duration REAL,
            moving_duration_seconds REAL,
            elapsed_duration REAL,
            elapsed_duration_seconds REAL,
            average_speed REAL,
            average_moving_speed REAL,
            max_speed REAL,
            calories REAL,
            bmr_calories REAL,
            average_hr REAL,
            max_hr REAL,
            average_swim_cadence REAL,
            number_of_active_lengths INTEGER,
            total_strokes INTEGER,
            average_strokes REAL,
            average_swolf REAL,
            average_stroke_distance REAL,
            swim_drill TEXT,
            -- New interval type fields
            interval_type TEXT,
            interval_duration REAL
        )
    """)
    
    
    # Create indexes for performance
    create_raw_indexes(conn)
    
    logger.info("Raw database tables created successfully")


def create_raw_indexes(conn: sqlite3.Connection) -> None:
    """
    Create indexes for better query performance on raw tables.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating raw database indexes...")
    
    indexes = [
        # Date-based queries
        "CREATE INDEX IF NOT EXISTS idx_raw_daily_summary_date ON raw_daily_summary(date)",
        "CREATE INDEX IF NOT EXISTS idx_raw_recovery_date ON raw_recovery(date)",
        "CREATE INDEX IF NOT EXISTS idx_raw_activities_date ON raw_activities(date)",
        "CREATE INDEX IF NOT EXISTS idx_raw_swimming_sessions_date ON raw_swimming_sessions(date)",
        
        # Foreign key lookups
        "CREATE INDEX IF NOT EXISTS idx_raw_swimming_laps_session ON raw_swimming_laps(session_id)",
        
        # Activity type queries
        "CREATE INDEX IF NOT EXISTS idx_raw_activities_type ON raw_activities(activity_type)",
        "CREATE INDEX IF NOT EXISTS idx_raw_activities_activity_id ON raw_activities(activity_id)",
        
        # Swimming-specific indexes
        "CREATE INDEX IF NOT EXISTS idx_raw_swimming_sessions_activity_id ON raw_swimming_sessions(activity_id)",
        "CREATE INDEX IF NOT EXISTS idx_raw_swimming_laps_interval_type ON raw_swimming_laps(interval_type)"
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)
    
    logger.info("Raw database indexes created successfully")


def drop_raw_tables(conn: sqlite3.Connection) -> None:
    """
    Drop all raw database tables (for testing/development).
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Dropping raw database tables...")
    
    tables = [
        "raw_swimming_laps", 
        "raw_swimming_sessions",
        "raw_activities",
        "raw_recovery",
        "raw_daily_summary"
    ]
    
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    
    logger.info("Raw database tables dropped successfully")


def get_raw_table_info(conn: sqlite3.Connection) -> List[dict]:
    """
    Get information about all raw tables in the database.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        List of table information dictionaries
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raw_%' ORDER BY name")
    tables = cursor.fetchall()
    
    table_info = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        table_info.append({
            'name': table_name,
            'columns': columns
        })
    
    return table_info
