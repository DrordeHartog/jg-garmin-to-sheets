"""
ETL-related CLI commands.
"""

import asyncio
import argparse
from datetime import date
from pathlib import Path
from typing import List, Dict, Any
from ..etl.orchestration.orchestrator import ETLOrchestrator
from ..etl.orchestration.config import OrchestratorConfig, NotificationConfig
from ..database.SQLiteManager import SQLiteManager

class ETLCommands:
    """ETL-related CLI commands."""
    
    def __init__(self):
        self.orchestrator = None
    
    async def initialize(self):
        """Initialize the orchestrator."""
        config = OrchestratorConfig(
            database_path="data/health_data.db",
            cache_dir="data/cache",
            rate_limits={},
            max_concurrent_jobs=3,
            notifications=NotificationConfig(webhook_url="")
        )
        self.orchestrator = ETLOrchestrator(config)
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.orchestrator:
            await self.orchestrator.stop()
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active jobs from the config table."""
        with SQLiteManager("data/health_data.db").get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id, job_name, processor_class, description 
                FROM etl_job_config 
                WHERE is_active = 1 
                ORDER BY job_id
            """)
            return [
                {
                    'job_id': row[0],
                    'job_name': row[1], 
                    'processor_class': row[2],
                    'description': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    async def _clear_processor_tables(self, active_jobs: List[Dict[str, Any]]):
        """Clear tables for active processors."""
        # Map processor classes to their corresponding table names
        processor_to_table = {
            'SwimmingSessionsProcessor': 'swimming_sessions',
            'SwimmingIntervalsProcessor': 'swimming_intervals', 
            'SwimmingLapsProcessor': 'swimming_laps',
            'RecoveryProcessor': 'recovery',
            'DailySummaryProcessor': 'daily_summary',
            'ActivitiesProcessor': 'activities'
        }
        
        # Define clearing order to respect foreign key constraints
        # Child tables (with foreign keys) must be cleared before parent tables
        clearing_order = [
            'swimming_laps',      # Has FK to swimming_sessions
            'swimming_intervals', # Has FK to swimming_sessions  
            'swimming_sessions',  # Parent table
            'recovery',
            'daily_summary',
            'activities'
        ]
        
        tables_to_clear = set()
        for job in active_jobs:
            processor_class = job['processor_class']
            if processor_class in processor_to_table:
                tables_to_clear.add(processor_to_table[processor_class])
        
        if tables_to_clear:
            with SQLiteManager("data/health_data.db").get_connection() as conn:
                cursor = conn.cursor()
                cleared_count = 0
                for table in clearing_order:
                    if table in tables_to_clear:
                        try:
                            cursor.execute(f"DELETE FROM {table}")
                            print(f"  ✅ Cleared {table} table")
                            cleared_count += 1
                        except Exception as e:
                            print(f"  ❌ Failed to clear {table} table: {e}")
                conn.commit()
                print(f"Cleared {cleared_count} tables")
    
    def _sort_jobs_by_dependency(self, active_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort jobs by dependency order to respect foreign key constraints."""
        # Define dependency order (parent tables before child tables)
        dependency_order = {
            'SwimmingSessionsProcessor': 1,  # Parent table
            'SwimmingIntervalsProcessor': 2, # Child of sessions
            'SwimmingLapsProcessor': 3,      # Child of sessions
            'RecoveryProcessor': 4,
            'DailySummaryProcessor': 5,
            'ActivitiesProcessor': 6
        }
        
        # Sort jobs by their dependency order
        return sorted(active_jobs, key=lambda job: dependency_order.get(job['processor_class'], 999))
    
    async def run_all_active_jobs(self, target_date: str = None, clear_tables: bool = False) -> Dict[str, Any]:
        """Run all active ETL jobs."""
        if not self.orchestrator:
            await self.initialize()
        
        active_jobs = self.get_active_jobs()
        if not active_jobs:
            return {
                'status': 'no_active_jobs',
                'message': 'No active jobs found in configuration',
                'results': []
            }
        
        # Clear tables if requested
        if clear_tables:
            print("Clearing existing data from tables...")
            await self._clear_processor_tables(active_jobs)
        
        print(f"Found {len(active_jobs)} active jobs:")
        for job in active_jobs:
            print(f"  - Job {job['job_id']}: {job['job_name']} - {job['description']}")
        
        results = []
        total_records = 0
        
        # Parse target date if provided
        parsed_date = None
        if target_date:
            try:
                parsed_date = date.fromisoformat(target_date)
            except ValueError:
                return {
                    'status': 'error',
                    'message': f'Invalid date format: {target_date}. Use YYYY-MM-DD format.',
                    'results': []
                }
        
        # Process by date to avoid foreign key conflicts
        if parsed_date:
            # Process specific date across all jobs
            for job in active_jobs:
                print(f"\nRunning job {job['job_id']}: {job['job_name']}...")
                try:
                    result = await self.orchestrator.trigger_etl_job(job['job_id'], parsed_date)
                    results.append({
                        'job_id': job['job_id'],
                        'job_name': job['job_name'],
                        'status': result.status.value,
                        'records_processed': result.records_processed,
                        'errors': result.errors
                    })
                    total_records += result.records_processed
                    print(f"  ✅ {result.records_processed} records processed")
                    
                except Exception as e:
                    error_msg = f"Failed to run job {job['job_id']}: {str(e)}"
                    print(f"  ❌ {error_msg}")
                    results.append({
                        'job_id': job['job_id'],
                        'job_name': job['job_name'],
                        'status': 'failed',
                        'records_processed': 0,
                        'errors': [error_msg]
                    })
        else:
            # Process all dates, but one date at a time across all jobs
            cached_files = list(Path("data/cache").glob("*.json"))
            if not cached_files:
                return {
                    'status': 'no_files',
                    'message': 'No cached files found',
                    'results': []
                }
            
            for cache_file in cached_files:
                date_str = cache_file.stem
                file_date = date.fromisoformat(date_str)
                print(f"\n=== Processing date: {date_str} ===")
                
                # Process this date across all active jobs
                for job in active_jobs:
                    print(f"Running job {job['job_id']}: {job['job_name']}...")
                    try:
                        result = await self.orchestrator.trigger_etl_job(job['job_id'], file_date)
                        results.append({
                            'job_id': job['job_id'],
                            'job_name': job['job_name'],
                            'date': date_str,
                            'status': result.status.value,
                            'records_processed': result.records_processed,
                            'errors': result.errors
                        })
                        total_records += result.records_processed
                        print(f"  ✅ {result.records_processed} records processed")
                        
                    except Exception as e:
                        error_msg = f"Failed to run job {job['job_id']} for {date_str}: {str(e)}"
                        print(f"  ❌ {error_msg}")
                        results.append({
                            'job_id': job['job_id'],
                            'job_name': job['job_name'],
                            'date': date_str,
                            'status': 'failed',
                            'records_processed': 0,
                            'errors': [error_msg]
                        })
        
        return {
            'status': 'completed',
            'message': f'Processed {len(active_jobs)} jobs with {total_records} total records',
            'total_records': total_records,
            'results': results
        }

def create_etl_parser() -> argparse.ArgumentParser:
    """Create ETL argument parser."""
    parser = argparse.ArgumentParser(description='ETL Commands')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # All command
    all_parser = subparsers.add_parser('all', help='Run all active ETL jobs')
    all_parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD format)')
    all_parser.add_argument('--clear', action='store_true', help='Clear existing data before processing')
    
    return parser

async def main():
    """Main CLI entry point."""
    parser = create_etl_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    etl_commands = ETLCommands()
    
    try:
        if args.command == 'all':
            result = await etl_commands.run_all_active_jobs(args.date, args.clear)
            
            print(f"\n{'='*50}")
            print(f"ETL Execution Summary")
            print(f"{'='*50}")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            
            if 'total_records' in result:
                print(f"Total Records: {result['total_records']}")
            
            if result['results']:
                print(f"\nJob Results:")
                for job_result in result['results']:
                    status_icon = "✅" if job_result['status'] == 'completed' else "❌"
                    print(f"  {status_icon} Job {job_result['job_id']} ({job_result['job_name']}): {job_result['records_processed']} records")
                    if job_result['errors']:
                        for error in job_result['errors']:
                            print(f"    Error: {error}")
    
    finally:
        await etl_commands.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
