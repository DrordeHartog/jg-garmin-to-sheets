"""
Database Migration Script
Renames current tables to raw_* schema and creates processed table schemas
"""

import sqlite3
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Handles database schema migration to separate raw and processed tables"""
    
    def __init__(self, db_path: str):
        """
        Initialize the migration
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = None
    
    def __enter__(self):
        """Context manager entry"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = OFF")  # Disable FK constraints during migration
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            self.conn.execute("PRAGMA foreign_keys = ON")  # Re-enable FK constraints
            self.conn.close()
    
    def get_existing_tables(self) -> List[str]:
        """
        Get list of existing tables in the database
        
        Returns:
            List of table names
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def rename_tables_to_raw(self) -> List[str]:
        """
        Rename current tables to raw_* schema
        
        Returns:
            List of renamed tables
        """
        logger.info("Starting table rename to raw_* schema...")
        
        existing_tables = self.get_existing_tables()
        renamed_tables = []
        
        # Tables to rename (excluding any that already start with raw_)
        tables_to_rename = [
            'daily_summary',
            'recovery', 
            'activities',
            'swimming_sessions',
            'swimming_laps'
        ]
        
        for table_name in tables_to_rename:
            if table_name in existing_tables:
                raw_table_name = f"raw_{table_name}"
                
                # Check if raw table already exists
                if raw_table_name in existing_tables:
                    logger.warning(f"Raw table {raw_table_name} already exists, skipping rename of {table_name}")
                    continue
                
                # Rename table
                self.conn.execute(f"ALTER TABLE {table_name} RENAME TO {raw_table_name}")
                renamed_tables.append(f"{table_name} -> {raw_table_name}")
                logger.info(f"Renamed {table_name} to {raw_table_name}")
        
        logger.info(f"Renamed {len(renamed_tables)} tables to raw_* schema")
        return renamed_tables
    
    def update_raw_swimming_laps_schema(self) -> bool:
        """
        Update raw_swimming_laps table to include new interval fields
        
        Returns:
            True if schema was updated, False if no changes needed
        """
        logger.info("Checking raw_swimming_laps schema for updates...")
        
        # Check if interval_type column exists
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(raw_swimming_laps)")
        columns = [row[1] for row in cursor.fetchall()]
        
        schema_updated = False
        
        if 'interval_type' not in columns:
            logger.info("Adding interval_type column to raw_swimming_laps")
            self.conn.execute("ALTER TABLE raw_swimming_laps ADD COLUMN interval_type TEXT")
            schema_updated = True
        
        if 'interval_duration' not in columns:
            logger.info("Adding interval_duration column to raw_swimming_laps")
            self.conn.execute("ALTER TABLE raw_swimming_laps ADD COLUMN interval_duration REAL")
            schema_updated = True
        
        if schema_updated:
            logger.info("Updated raw_swimming_laps schema with interval fields")
        else:
            logger.info("raw_swimming_laps schema is up to date")
        
        return schema_updated
    
    def create_processed_tables(self) -> List[str]:
        """
        Create processed table schemas
        
        Returns:
            List of created processed tables
        """
        logger.info("Creating processed table schemas...")
        
        # Import the processed schema functions
        from ...database.processed_schema import create_processed_tables
        
        # Create processed tables
        create_processed_tables(self.conn)
        
        # Get list of processed tables
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'processed_%' ORDER BY name")
        processed_tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Created {len(processed_tables)} processed tables")
        return processed_tables
    
    def run_migration(self) -> Dict[str, Any]:
        """
        Run complete database migration
        
        Returns:
            Migration results summary
        """
        logger.info("Starting database migration to raw/processed schema...")
        
        results = {
            'renamed_tables': [],
            'schema_updates': [],
            'created_processed_tables': [],
            'errors': []
        }
        
        try:
            # Step 1: Rename existing tables to raw_*
            results['renamed_tables'] = self.rename_tables_to_raw()
            
            # Step 2: Update raw_swimming_laps schema if needed
            if self.update_raw_swimming_laps_schema():
                results['schema_updates'].append('raw_swimming_laps updated with interval fields')
            
            # Step 3: Create processed tables
            results['created_processed_tables'] = self.create_processed_tables()
            
            # Commit all changes
            self.conn.commit()
            
            logger.info("Database migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            results['errors'].append(str(e))
            self.conn.rollback()
            raise
        
        return results
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate that migration was successful
        
        Returns:
            Validation results
        """
        logger.info("Validating migration...")
        
        validation_results = {
            'raw_tables': [],
            'processed_tables': [],
            'schema_validation': {},
            'errors': []
        }
        
        try:
            # Check raw tables
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raw_%' ORDER BY name")
            validation_results['raw_tables'] = [row[0] for row in cursor.fetchall()]
            
            # Check processed tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'processed_%' ORDER BY name")
            validation_results['processed_tables'] = [row[0] for row in cursor.fetchall()]
            
            # Validate raw_swimming_laps schema
            if 'raw_swimming_laps' in validation_results['raw_tables']:
                cursor.execute("PRAGMA table_info(raw_swimming_laps)")
                columns = [row[1] for row in cursor.fetchall()]
                validation_results['schema_validation']['raw_swimming_laps'] = {
                    'has_interval_type': 'interval_type' in columns,
                    'has_interval_duration': 'interval_duration' in columns,
                    'total_columns': len(columns)
                }
            
            logger.info("Migration validation completed successfully")
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            validation_results['errors'].append(str(e))
        
        return validation_results


def run_migration(db_path: str) -> Dict[str, Any]:
    """
    Convenience function to run the migration
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        Migration results
    """
    with DatabaseMigration(db_path) as migration:
        return migration.run_migration()


def validate_migration(db_path: str) -> Dict[str, Any]:
    """
    Convenience function to validate the migration
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        Validation results
    """
    with DatabaseMigration(db_path) as migration:
        return migration.validate_migration()
