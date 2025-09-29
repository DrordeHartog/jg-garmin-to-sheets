"""
Database schema definitions for the swimming analyzer.

This module contains all table creation and schema management functions.
"""

import sqlite3
import logging
from typing import List

logger = logging.getLogger(__name__)


def create_tables(conn: sqlite3.Connection) -> None:
    """
    Create all database tables with proper relationships and indexes.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating database tables...")
    
    # 1. Daily Summary Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
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
    
    # 2. Recovery Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recovery (
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
    
    # 3. Activities Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            activity_id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            activity_type TEXT NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            duration_seconds INTEGER,
            distance_meters REAL,
            calories INTEGER,
            average_hr REAL,
            max_hr REAL,
            FOREIGN KEY (date) REFERENCES daily_summary(date)
        )
    """)
    
    # 4. Swimming Sessions Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS swimming_sessions (
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
            swim_anaerobic_training_effect REAL,
            FOREIGN KEY (date) REFERENCES daily_summary(date)
        )
    """)
    
    # 5. Swimming Intervals Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS swimming_intervals (
            interval_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            interval_type TEXT NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            duration_seconds REAL,
            moving_duration_seconds REAL,
            elapsed_duration_seconds REAL,
            distance_meters REAL,
            average_speed REAL,
            calories REAL,
            bmr_calories REAL,
            average_hr REAL,
            max_hr REAL,
            total_exercise_reps INTEGER,
            message_index INTEGER,
            FOREIGN KEY (session_id) REFERENCES swimming_sessions(session_id)
        )
    """)
    
    # 6. Swimming Laps Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS swimming_laps (
            lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interval_id INTEGER NOT NULL,
            lap_index INTEGER NOT NULL,
            start_time DATETIME,
            distance_meters REAL,
            duration_seconds REAL,
            moving_duration_seconds REAL,
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
            FOREIGN KEY (interval_id) REFERENCES swimming_intervals(interval_id)
        )
    """)
    
    # 7. Swimming Lengths Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS swimming_lengths (
            length_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lap_id INTEGER NOT NULL,
            length_index INTEGER NOT NULL,
            start_time DATETIME,
            distance_meters REAL,
            duration_seconds REAL,
            average_speed REAL,
            max_speed REAL,
            average_hr REAL,
            max_hr REAL,
            total_strokes INTEGER,
            swim_stroke TEXT,
            FOREIGN KEY (lap_id) REFERENCES swimming_laps(lap_id)
        )
    """)
    
    # Create indexes for performance
    create_indexes(conn)
    
    logger.info("Database tables created successfully")


def create_indexes(conn: sqlite3.Connection) -> None:
    """
    Create indexes for better query performance.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating database indexes...")
    
    indexes = [
        # Date-based queries
        "CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_summary(date)",
        "CREATE INDEX IF NOT EXISTS idx_recovery_date ON recovery(date)",
        "CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)",
        "CREATE INDEX IF NOT EXISTS idx_swimming_sessions_date ON swimming_sessions(date)",
        
        # Foreign key lookups
        "CREATE INDEX IF NOT EXISTS idx_swimming_intervals_session ON swimming_intervals(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_swimming_laps_interval ON swimming_laps(interval_id)",
        "CREATE INDEX IF NOT EXISTS idx_swimming_lengths_lap ON swimming_lengths(lap_id)",
        
        # Activity type queries
        "CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type)",
        "CREATE INDEX IF NOT EXISTS idx_activities_activity_id ON activities(activity_id)",
        
        # Swimming-specific indexes
        "CREATE INDEX IF NOT EXISTS idx_swimming_sessions_activity_id ON swimming_sessions(activity_id)",
        "CREATE INDEX IF NOT EXISTS idx_swimming_intervals_type ON swimming_intervals(interval_type)"
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)
    
    logger.info("Database indexes created successfully")


def drop_tables(conn: sqlite3.Connection) -> None:
    """
    Drop all database tables (for testing/development).
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Dropping database tables...")
    
    tables = [
        "swimming_lengths",
        "swimming_laps", 
        "swimming_intervals",
        "swimming_sessions",
        "activities",
        "recovery",
        "daily_summary"
    ]
    
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    
    logger.info("Database tables dropped successfully")


def get_table_info(conn: sqlite3.Connection) -> List[dict]:
    """
    Get information about all tables in the database.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        List of table information dictionaries
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
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