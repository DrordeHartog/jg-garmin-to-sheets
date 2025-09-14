"""
Integration test for swimming ETL load methods.
Tests the complete extract -> transform -> load pipeline and cleans up afterward.
"""

import asyncio
import logging
import json
from datetime import date
from pathlib import Path
import sys
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.etl.processing.processors.swimming_sessions_processor import SwimmingSessionsProcessor
from src.etl.processing.processors.swimming_intervals_processor import SwimmingIntervalsProcessor
from src.etl.processing.processors.swimming_laps_processor import SwimmingLapsProcessor
from src.database.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/swimming_load_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SwimmingLoadTester:
    """Test class for swimming ETL load methods."""
    
    def __init__(self):
        # Use the existing health_data.db instead of the default swimming_analyzer.db
        self.db_manager = DatabaseManager("data/health_data.db")
        self.test_date = date(2025, 9, 12)
        self.cache_dir = Path("data/cache")
        
        # Initialize processors
        self.sessions_processor = SwimmingSessionsProcessor()
        self.intervals_processor = SwimmingIntervalsProcessor()
        self.laps_processor = SwimmingLapsProcessor()
    
    def _load_from_cache(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Load raw data from cache if it exists."""
        cache_file = self.cache_dir / f"{target_date}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    raw_data = json.load(f)
                logger.info(f"Loaded cached data for {target_date} ({cache_file.stat().st_size / 1024:.1f} KB)")
                return raw_data
            except Exception as e:
                logger.warning(f"Failed to load cache for {target_date}: {e}")
                return None
        return None
    
    async def test_complete_etl_pipeline(self):
        """Test complete ETL pipeline: extract -> transform -> load."""
        logger.info(f"Starting complete ETL pipeline test for {self.test_date}")
        
        try:
            # Load cached data
            raw_data = self._load_from_cache(self.test_date)
            if not raw_data:
                logger.error(f"No cached data found for {self.test_date}")
                return False
            
            logger.info(f"Loaded cached data for {self.test_date}")
            
            # Test Sessions ETL
            logger.info("=== Testing SwimmingSessions ETL ===")
            sessions_count = await self.sessions_processor.run(raw_data, self.test_date, self.db_manager)
            logger.info(f"Sessions ETL completed: {sessions_count} records loaded")
            
            # Test Intervals ETL
            logger.info("=== Testing SwimmingIntervals ETL ===")
            intervals_count = await self.intervals_processor.run(raw_data, self.test_date, self.db_manager)
            logger.info(f"Intervals ETL completed: {intervals_count} records loaded")
            
            # Test Laps ETL
            logger.info("=== Testing SwimmingLaps ETL ===")
            laps_count = await self.laps_processor.run(raw_data, self.test_date, self.db_manager)
            logger.info(f"Laps ETL completed: {laps_count} records loaded")
            
            # Verify data in database
            await self.verify_database_data()
            
            return True
            
        except Exception as e:
            logger.error(f"ETL pipeline test failed: {str(e)}")
            return False
    
    async def verify_database_data(self):
        """Verify that data was correctly loaded into database."""
        logger.info("=== Verifying Database Data ===")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check sessions
            cursor.execute("SELECT COUNT(*) FROM swimming_sessions WHERE date = ?", (self.test_date.isoformat(),))
            sessions_count = cursor.fetchone()[0]
            logger.info(f"Database sessions count: {sessions_count}")
            
            # Check intervals
            cursor.execute("SELECT COUNT(*) FROM swimming_intervals")
            intervals_count = cursor.fetchone()[0]
            logger.info(f"Database intervals count: {intervals_count}")
            
            # Check laps
            cursor.execute("SELECT COUNT(*) FROM swimming_laps")
            laps_count = cursor.fetchone()[0]
            logger.info(f"Database laps count: {laps_count}")
            
            # Show sample data
            if sessions_count > 0:
                cursor.execute("SELECT session_id, total_distance_meters, total_duration_seconds FROM swimming_sessions WHERE date = ? LIMIT 1", (self.test_date.isoformat(),))
                sample_session = cursor.fetchone()
                logger.info(f"Sample session: {sample_session}")
            
            if intervals_count > 0:
                cursor.execute("SELECT interval_id, session_id, interval_type, duration_seconds FROM swimming_intervals ORDER BY interval_id")
                sample_intervals = cursor.fetchall()
                logger.info(f"All intervals: {sample_intervals}")
            
            if laps_count > 0:
                # Show laps data (no more interval mapping needed)
                cursor.execute("""
                    SELECT l.lap_index, l.session_id, l.distance_meters, l.duration_seconds, l.swim_drill, l.start_time
                    FROM swimming_laps l 
                    ORDER BY l.lap_index
                """)
                lap_data = cursor.fetchall()
                logger.info("=== LAPS DATA ===")
                for row in lap_data:
                    logger.info(f"Lap {row[0]}: Session {row[1]} - {row[2]}m, {row[3]}s, drill: {row[4]}, start: {row[5]}")
                
                # Show sample laps
                cursor.execute("SELECT lap_index, session_id, distance_meters, duration_seconds FROM swimming_laps ORDER BY lap_index LIMIT 5")
                sample_laps = cursor.fetchall()
                logger.info(f"Sample laps: {sample_laps}")
    
    async def cleanup_test_data(self):
        """Clean up test data from database."""
        logger.info("=== Cleaning up test data ===")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete in reverse order due to foreign key constraints
            cursor.execute("DELETE FROM swimming_laps")
            cursor.execute("DELETE FROM swimming_intervals")
            cursor.execute("DELETE FROM swimming_sessions WHERE date = ?", (self.test_date.isoformat(),))
            
            conn.commit()
            
            logger.info("Test data cleaned up successfully")


async def main():
    """Main test function."""
    tester = SwimmingLoadTester()
    
    try:
        # Run the complete ETL test
        success = await tester.test_complete_etl_pipeline()
        
        if success:
            logger.info("✅ ETL pipeline test completed successfully!")
        else:
            logger.error("❌ ETL pipeline test failed!")
            return
        
        # Clean up test data
        await tester.cleanup_test_data()
        logger.info("✅ Test cleanup completed!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        # Still try to clean up
        try:
            await tester.cleanup_test_data()
        except Exception as cleanup_error:
            logger.error(f"Cleanup also failed: {str(cleanup_error)}")


if __name__ == "__main__":
    asyncio.run(main())
