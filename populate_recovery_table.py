#!/usr/bin/env python3
"""
Script to populate the recovery table with real Garmin data.

This script will:
1. Create a database
2. Fetch recovery data from Garmin API for a date range
3. Process and store the data using RecoveryProcessor
4. Show progress and results
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.database_manager import DatabaseManager
from src.database.schema import create_tables
from src.orchestration.processors.recovery_processor import RecoveryProcessor
from src.core.garmin_client import GarminClient
from src.utils.logging_config import setup_custom_logging
import logging

logger = logging.getLogger(__name__)

async def populate_recovery_table(dates_to_process: List[date], email: str, password: str, db_path: str = "health_data.db"):
    """
    Populate the recovery table with Garmin data for the specified dates.
    
    Args:
        dates_to_process: List of dates to process
        email: Garmin email
        password: Garmin password
        db_path: Path to SQLite database file
    """
    
    # Setup logging with debug level to see what's happening
    setup_custom_logging(level="DEBUG", output="both", log_file="logs/recovery_population.log")
    logger.info(f"Starting recovery table population for {len(dates_to_process)} dates")
    
    # Initialize database
    db_manager = DatabaseManager(db_path)
    with db_manager.get_connection() as conn:
        create_tables(conn)
    logger.info(f"Database initialized at {db_path}")
    
    # Initialize processor and client
    processor = RecoveryProcessor()
    garmin_client = GarminClient()
    
    # Track progress
    total_days = len(dates_to_process)
    successful_days = 0
    failed_days = 0
    
    logger.info(f"Processing {total_days} days of data...")
    
    # Process each day
    for current_date in dates_to_process:
        try:
            logger.info(f"Processing {current_date} ({successful_days + failed_days + 1}/{total_days})")
            
            # Authenticate before fetching data (credentials are passed each time)
            await garmin_client.authenticate(email, password)
            
            # Fetch raw data for the day
            raw_data = await garmin_client._fetch_raw_data(current_date)
            logger.debug(f"Raw data for {current_date}: {raw_data}")
            
            # Process with RecoveryProcessor
            extracted_data = processor.extract(raw_data, current_date)
            transformed_data = processor.transform(extracted_data, current_date)
            logger.debug(f"Transformed data for {current_date}: {transformed_data}")
            
            if transformed_data:
                # Load into database
                records_loaded = await processor.load(transformed_data, db_manager)
                if records_loaded > 0:
                    successful_days += 1
                    logger.info(f"✅ {current_date}: {records_loaded} record(s) loaded")
                else:
                    failed_days += 1
                    logger.warning(f"⚠️  {current_date}: No records loaded")
            else:
                failed_days += 1
                logger.warning(f"⚠️  {current_date}: No data to process")
                
        except Exception as e:
            failed_days += 1
            logger.error(f"❌ {current_date}: Error - {str(e)}")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    # Summary
    logger.info(f"\n📊 POPULATION SUMMARY:")
    logger.info(f"Total days processed: {total_days}")
    logger.info(f"Successful: {successful_days}")
    logger.info(f"Failed: {failed_days}")
    logger.info(f"Success rate: {(successful_days/total_days)*100:.1f}%")
    
    # Verify data in database
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recovery")
        total_records = cursor.fetchone()[0]
        logger.info(f"Total records in recovery table: {total_records}")
        
        # Show sample data
        cursor.execute("SELECT date, sleep_score, hrv_status, average_stress FROM recovery ORDER BY date DESC LIMIT 5")
        sample_data = cursor.fetchall()
        logger.info(f"Sample data (latest 5 records):")
        for record in sample_data:
            logger.info(f"  {record[0]}: Sleep={record[1]}, HRV={record[2]}, Stress={record[3]}")

def check_existing_data(db_manager: DatabaseManager, start_date: date, end_date: date) -> Dict[str, int]:
    """Check which dates already have data in the database."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, COUNT(*) as record_count 
            FROM recovery 
            WHERE date BETWEEN ? AND ? 
            GROUP BY date
        """, (start_date.isoformat(), end_date.isoformat()))
        
        existing_data = {row[0]: row[1] for row in cursor.fetchall()}
        return existing_data

def get_missing_dates(start_date: date, end_date: date, existing_data: Dict[str, int]) -> List[date]:
    """Get list of dates that need to be imported."""
    missing_dates = []
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.isoformat() not in existing_data:
            missing_dates.append(current_date)
        current_date += timedelta(days=1)
    
    return missing_dates

def main():
    """Main function to run the population script."""
    
    # Configuration - Full population from July 24, 2025
    START_DATE = date(2025, 7, 24)  # July 24, 2025
    END_DATE = date.today()
    
    # Check existing data first
    db_manager = DatabaseManager("data/health_data.db")
    
    # Create database and tables if they don't exist
    with db_manager.get_connection() as conn:
        create_tables(conn)
    
    existing_data = check_existing_data(db_manager, START_DATE, END_DATE)
    missing_dates = get_missing_dates(START_DATE, END_DATE, existing_data)
    
    if not missing_dates:
        print("✅ All data already imported!")
        return
    
    print(f"📊 Found {len(existing_data)} existing records")
    print(f"🔄 Need to import {len(missing_dates)} missing dates")
    print(f"📅 Missing dates: {missing_dates[0]} to {missing_dates[-1]}")
    
    # Get credentials from user
    print("\n🔐 Garmin Credentials Required")
    email = input("Enter your Garmin email: ").strip()
    password = input("Enter your Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        sys.exit(1)
    
    print(f"\n📅 Date Range: {START_DATE} to {END_DATE}")
    print(f"📊 Total days: {(END_DATE - START_DATE).days + 1}")
    
    confirm = input("\nProceed with data population? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Population cancelled.")
        sys.exit(0)
    
    # Run the population
    try:
        asyncio.run(populate_recovery_table(missing_dates, email, password))
        print("\n✅ Recovery table population completed!")
    except KeyboardInterrupt:
        print("\n⏹️  Population interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during population: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
