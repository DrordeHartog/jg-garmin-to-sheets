"""
Create metrics configuration table.

This script creates the metric_config table for flexible metric management.
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_metrics_config_table(db_path: str = None) -> bool:
    """
    Create the metrics configuration table.
    
    Args:
        db_path: Path to SQLite database. If None, uses default location.
        
    Returns:
        bool: True if table was created successfully
    """
    if db_path is None:
        # Default database location
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "data" / "swimming_analyzer.db"
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # Create metrics configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    api_endpoint TEXT NOT NULL,
                    api_field_path TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    unit TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    version INTEGER DEFAULT 1,
                    parent_metric_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_metric_id) REFERENCES metric_config(id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_config_source 
                ON metric_config(source)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_config_active 
                ON metric_config(is_active)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_config_name_source 
                ON metric_config(metric_name, source)
            """)
            
            conn.commit()
            logger.info("Metrics configuration table created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to create metrics configuration table: {e}")
        return False


def create_etl_job_config_table(db_path: str = None) -> bool:
    """
    Create the ETL job configuration table.
    
    Args:
        db_path: Path to SQLite database. If None, uses default location.
        
    Returns:
        bool: True if table was created successfully
    """
    if db_path is None:
        # Default database location
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "data" / "swimming_analyzer.db"
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # Create ETL job configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etl_job_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    job_name TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    processor_class TEXT NOT NULL,
                    job_module TEXT NOT NULL,
                    description TEXT,
                    schedule TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    priority INTEGER DEFAULT 1,
                    retry_count INTEGER DEFAULT 3,
                    timeout_seconds INTEGER DEFAULT 1800,
                    config_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_etl_job_config_job_id 
                ON etl_job_config(job_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_etl_job_config_active 
                ON etl_job_config(is_active)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_etl_job_config_type 
                ON etl_job_config(job_type)
            """)
            
            conn.commit()
            logger.info("ETL job configuration table created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to create ETL job configuration table: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Creating configuration tables...")
    
    success1 = create_metrics_config_table()
    success2 = create_etl_job_config_table()
    
    if success1 and success2:
        print("✅ All configuration tables created successfully!")
    else:
        print("❌ Some tables failed to create. Check logs for details.")
