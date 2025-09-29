"""
Processed database schema definitions for the swimming analyzer.

This module contains processed table creation and schema management functions.
Processed tables store analysis-ready data with computed metrics and aggregations.
"""

import sqlite3
import logging
from typing import List

logger = logging.getLogger(__name__)


def create_processed_tables(conn: sqlite3.Connection) -> None:
    """
    Create all processed database tables with proper relationships and indexes.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating processed database tables...")
    
    # 1. Processed Swimming Sessions Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_swimming_sessions (
            session_id TEXT PRIMARY KEY,
            date DATE NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            total_distance_meters REAL,
            total_duration_seconds INTEGER,
            pool_length_meters REAL,
            -- Computed metrics
            avg_pace_per_100m REAL,
            max_pace_per_100m REAL,
            avg_speed REAL,
            max_speed REAL,
            avg_hr REAL,
            max_hr REAL,
            total_strokes INTEGER,
            avg_strokes_per_length REAL,
            avg_strokes_per_minute REAL,
            avg_cadence REAL,
            avg_swolf REAL,
            min_swolf REAL,
            max_swolf REAL,
            total_calories INTEGER,
            training_effect REAL,
            anaerobic_training_effect REAL,
            -- Data quality flags
            is_valid_session BOOLEAN DEFAULT 1,
            data_quality_score REAL,
            -- Aggregated lap metrics
            total_laps INTEGER,
            active_laps INTEGER,
            rest_laps INTEGER,
            drill_laps INTEGER,
            -- Interval breakdown
            warmup_distance REAL,
            active_distance REAL,
            rest_distance REAL,
            cooldown_distance REAL,
            warmup_duration REAL,
            active_duration REAL,
            rest_duration REAL,
            cooldown_duration REAL
        )
    """)
    
    # 2. Processed Swimming Laps Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_swimming_laps (
            lap_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            lap_index INTEGER NOT NULL,
            start_time DATETIME,
            distance REAL,
            duration_seconds REAL,
            moving_duration_seconds REAL,
            elapsed_duration_seconds REAL,
            -- Computed metrics
            pace_per_100m REAL,
            speed REAL,
            calories REAL,
            average_hr REAL,
            max_hr REAL,
            stroke_count INTEGER,
            strokes_per_minute REAL,
            swolf REAL,
            stroke_distance REAL,
            -- Data quality flags
            is_rest_lap BOOLEAN DEFAULT 0,
            is_valid_distance BOOLEAN DEFAULT 1,
            is_valid_pace BOOLEAN DEFAULT 1,
            is_valid_hr BOOLEAN DEFAULT 1,
            -- Interval context
            interval_type TEXT,
            interval_duration REAL,
            -- Drill information
            swim_drill TEXT,
            drill_type TEXT
        )
    """)
    
    # 3. Processed Swimming Weekly Summary Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_swimming_weekly_summary (
            week_start_date DATE PRIMARY KEY,
            week_end_date DATE NOT NULL,
            year INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            -- Weekly totals
            total_sessions INTEGER,
            total_distance_meters REAL,
            total_duration_seconds INTEGER,
            total_calories INTEGER,
            total_strokes INTEGER,
            -- Weekly averages
            avg_sessions_per_week REAL,
            avg_distance_per_session REAL,
            avg_duration_per_session REAL,
            avg_pace_per_100m REAL,
            avg_speed REAL,
            avg_hr REAL,
            avg_strokes_per_session REAL,
            avg_swolf REAL,
            -- Weekly trends
            pace_trend REAL,
            distance_trend REAL,
            hr_trend REAL,
            swolf_trend REAL,
            -- Data quality
            data_quality_score REAL,
            sessions_with_issues INTEGER
        )
    """)
    
    # 4. Processed Swimming Monthly Summary Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_swimming_monthly_summary (
            month_start_date DATE PRIMARY KEY,
            month_end_date DATE NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            -- Monthly totals
            total_sessions INTEGER,
            total_distance_meters REAL,
            total_duration_seconds INTEGER,
            total_calories INTEGER,
            total_strokes INTEGER,
            -- Monthly averages
            avg_sessions_per_week REAL,
            avg_distance_per_session REAL,
            avg_duration_per_session REAL,
            avg_pace_per_100m REAL,
            avg_speed REAL,
            avg_hr REAL,
            avg_strokes_per_session REAL,
            avg_swolf REAL,
            -- Monthly trends
            pace_trend REAL,
            distance_trend REAL,
            hr_trend REAL,
            swolf_trend REAL,
            -- Data quality
            data_quality_score REAL,
            sessions_with_issues INTEGER
        )
    """)
    
    # Create indexes for performance
    create_processed_indexes(conn)
    
    logger.info("Processed database tables created successfully")


def create_processed_indexes(conn: sqlite3.Connection) -> None:
    """
    Create indexes for better query performance on processed tables.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating processed database indexes...")
    
    indexes = [
        # Date-based queries
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_sessions_date ON processed_swimming_sessions(date)",
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_laps_session ON processed_swimming_laps(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_processed_weekly_summary_week ON processed_swimming_weekly_summary(week_start_date)",
        "CREATE INDEX IF NOT EXISTS idx_processed_monthly_summary_month ON processed_swimming_monthly_summary(month_start_date)",
        
        # Performance queries
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_sessions_pace ON processed_swimming_sessions(avg_pace_per_100m)",
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_sessions_distance ON processed_swimming_sessions(total_distance_meters)",
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_laps_pace ON processed_swimming_laps(pace_per_100m)",
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_laps_interval_type ON processed_swimming_laps(interval_type)",
        
        # Data quality queries
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_sessions_quality ON processed_swimming_sessions(data_quality_score)",
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_laps_quality ON processed_swimming_laps(is_valid_pace, is_valid_hr)",
        
        # Drill analysis
        "CREATE INDEX IF NOT EXISTS idx_processed_swimming_laps_drill ON processed_swimming_laps(swim_drill, drill_type)"
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)
    
    logger.info("Processed database indexes created successfully")


def drop_processed_tables(conn: sqlite3.Connection) -> None:
    """
    Drop all processed database tables (for testing/development).
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Dropping processed database tables...")
    
    tables = [
        "processed_swimming_monthly_summary",
        "processed_swimming_weekly_summary",
        "processed_swimming_laps",
        "processed_swimming_sessions"
    ]
    
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    
    logger.info("Processed database tables dropped successfully")


def get_processed_table_info(conn: sqlite3.Connection) -> List[dict]:
    """
    Get information about all processed tables in the database.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        List of table information dictionaries
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'processed_%' ORDER BY name")
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
