"""
Main ETL orchestrator with APScheduler integration.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json
import os
from pathlib import Path
from .config import OrchestratorConfig, JobConfig, JobResult, JobStatus
from .load_manager import LoadManager
from .job_manager import JobManager
from .webhook_api import WebhookAPI

class ETLOrchestrator:
    """Main orchestrator for ETL pipeline with scheduling and load management."""
    
    def __init__(self, config: OrchestratorConfig):
        """Initialize the ETL orchestrator."""
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.load_manager = LoadManager(config.rate_limits)
        self.job_manager = JobManager(config.max_concurrent_jobs)
        self.webhook_api = WebhookAPI(self)
        
        # Initialize database manager for ETL operations
        from ...database.database_manager import DatabaseManager
        self.db_manager = DatabaseManager(config.database_path)
        
        # Initialize recovery processor for ETL operations
        from ..processing.processors.recovery_processor import RecoveryProcessor
        self.recovery_processor = RecoveryProcessor()
        
        # Initialize Garmin client for data fetching
        from ...ingestion.garmin_client import GarminClient
        self.garmin_client = GarminClient()
        
        # Initialize cache directory and settings
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size_mb = 100  # 100MB cache limit
        
        # Setup logging
        import logging
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"ETL Orchestrator initialized with database: {config.database_path}")
        
    async def start(self) -> None:
        """Start the orchestrator and all services."""
        try:
            self.logger.info("Starting ETL Orchestrator...")
            
            # Database is already initialized in DatabaseManager.__init__
            self.logger.info("Database ready")
            
            # Start scheduler (will be used in Step 4)
            # self.scheduler.start()
            # self.logger.info("Scheduler started")
            
            # Start webhook API (will be used in Step 5)
            # await self.webhook_api.start_server()
            # self.logger.info("Webhook API started")
            
            self.logger.info("ETL Orchestrator started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start ETL Orchestrator: {e}")
            raise
        
    async def stop(self) -> None:
        """Gracefully stop the orchestrator."""
        try:
            self.logger.info("Stopping ETL Orchestrator...")
            
            # Stop scheduler (will be used in Step 4)
            # if self.scheduler.running:
            #     self.scheduler.shutdown()
            #     self.logger.info("Scheduler stopped")
            
            # Stop webhook API (will be used in Step 5)
            # await self.webhook_api.stop_server()
            # self.logger.info("Webhook API stopped")
            
            # Close database connections
            # Database connections are managed by context managers, so no explicit cleanup needed
            
            self.logger.info("ETL Orchestrator stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping ETL Orchestrator: {e}")
            raise
        
    async def trigger_etl_job(self, job_id: int, target_date: Optional[date] = None) -> JobResult:
        """Manually trigger an ETL job by ID."""
        try:
            # Query job config from database
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_name, processor_class, description 
                    FROM etl_job_config 
                    WHERE job_id = ? AND is_active = 1
                """, (job_id,))
                job_config = cursor.fetchone()
            
            if not job_config:
                return JobResult(
                    job_id=f"manual_{job_id}",
                    status=JobStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_ms=0.0,
                    records_processed=0,
                    errors=[f"Job ID {job_id} not found or inactive"]
                )
            
            job_name, processor_class, description = job_config
            self.logger.info(f"Triggering job {job_id}: {job_name} - {description}")
            
            # Check if it's an orchestrator method or individual processor
            if processor_class.startswith('execute_'):
                # It's an orchestrator method (e.g., execute_swimming_etl)
                method = getattr(self, processor_class)
                return await method()
            else:
                # It's an individual processor (e.g., SwimmingSessionsProcessor)
                return await self._run_individual_processor(processor_class, target_date)
                
        except Exception as e:
            self.logger.error(f"Failed to trigger job {job_id}: {str(e)}")
            return JobResult(
                job_id=f"manual_{job_id}",
                status=JobStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=0,
                errors=[f"Job trigger failed: {str(e)}"]
            )
        
    async def schedule_etl_job(self, job_config: JobConfig) -> str:
        """Schedule a new ETL job."""
        # TODO: Implement job scheduling
        pass
        
    async def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Get status of a specific job."""
        # TODO: Implement job status retrieval
        pass
        
    async def list_jobs(self) -> List[JobResult]:
        """List all jobs (active and completed)."""
        # TODO: Implement jobs listing
        pass
        
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or scheduled job."""
        # TODO: Implement job cancellation
        pass
        
    def schedule_daily_jobs(self) -> None:
        """Schedule daily ETL jobs."""
        # TODO: Implement daily job scheduling
        pass
        
    def schedule_health_checks(self) -> None:
        """Schedule system health checks."""
        # TODO: Implement health check scheduling
        pass
        
    async def authenticate_garmin(self, email: str, password: str) -> bool:
        """Authenticate with Garmin API."""
        try:
            self.logger.info("Authenticating with Garmin API")
            await self.garmin_client.authenticate(email, password)
            self.logger.info("Garmin authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"Garmin authentication failed: {e}")
            return False
    
    def _get_cache_file_path(self, target_date: date) -> Path:
        """Get the cache file path for a given date."""
        return self.cache_dir / f"{target_date}.json"
    
    def _load_from_cache(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Load raw data from cache if it exists."""
        cache_file = self._get_cache_file_path(target_date)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    raw_data = json.load(f)
                self.logger.info(f"Loaded cached data for {target_date} ({cache_file.stat().st_size / 1024:.1f} KB)")
                return raw_data
            except Exception as e:
                self.logger.warning(f"Failed to load cache for {target_date}: {e}")
                return None
        return None
    
    def _save_to_cache(self, target_date: date, raw_data: Dict[str, Any]) -> None:
        """Save raw data to cache and manage cache size."""
        cache_file = self._get_cache_file_path(target_date)
        
        try:
            # Save to cache
            with open(cache_file, 'w') as f:
                json.dump(raw_data, f, indent=2)
            
            file_size_kb = cache_file.stat().st_size / 1024
            self.logger.info(f"Cached data for {target_date} ({file_size_kb:.1f} KB)")
            
            # Check cache size and cleanup if needed
            self._cleanup_cache_if_needed()
            
        except Exception as e:
            self.logger.error(f"Failed to save cache for {target_date}: {e}")
    
    def _cleanup_cache_if_needed(self) -> None:
        """Clean up cache files if total size exceeds limit."""
        try:
            # Calculate total cache size
            total_size_mb = sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (1024 * 1024)
            
            if total_size_mb > self.max_cache_size_mb:
                self.logger.info(f"Cache size ({total_size_mb:.1f} MB) exceeds limit ({self.max_cache_size_mb} MB), cleaning up...")
                
                # Get all cache files sorted by modification time (oldest first)
                cache_files = sorted(
                    self.cache_dir.glob("*.json"),
                    key=lambda f: f.stat().st_mtime
                )
                
                # Remove oldest files until under limit
                for cache_file in cache_files:
                    if total_size_mb <= self.max_cache_size_mb * 0.8:  # Clean to 80% of limit
                        break
                    
                    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
                    cache_file.unlink()
                    total_size_mb -= file_size_mb
                    self.logger.info(f"Removed old cache file: {cache_file.name}")
                
                self.logger.info(f"Cache cleanup complete. New size: {total_size_mb:.1f} MB")
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")
    
    async def _fetch_detailed_swimming_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch detailed swimming data for all swimming activities in the raw data."""
        if not raw_data or 'activities' not in raw_data:
            return raw_data
        
        # Find all swimming activities
        swimming_activities = [
            activity for activity in raw_data['activities'] 
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        if not swimming_activities:
            self.logger.info("No swimming activities found, skipping detailed data fetch")
            return raw_data
        
        self.logger.info(f"Found {len(swimming_activities)} swimming activities, fetching detailed data...")
        
        # Fetch detailed data for each swimming activity
        for i, activity in enumerate(swimming_activities):
            activity_id = activity.get('activityId')
            activity_name = activity.get('activityName', 'Unknown')
            
            if not activity_id:
                self.logger.warning(f"Skipping swimming activity {i+1}: no activity ID")
                continue
            
            try:
                # Check rate limits before making API calls
                if not await self.load_manager.can_make_request("garmin"):
                    self.logger.warning("Rate limit reached, waiting...")
                    await self.load_manager.wait_for_rate_limit("garmin")
                
                self.logger.info(f"Fetching detailed data for swimming activity: {activity_name} (ID: {activity_id})")
                
                # Fetch detailed swimming data using the already authenticated client
                try:
                    splits_data = self.garmin_client.client.get_activity_splits(activity_id)
                    split_summaries = self.garmin_client.client.get_activity_split_summaries(activity_id)
                    typed_splits = self.garmin_client.client.get_activity_typed_splits(activity_id)
                    
                    detailed_data = {
                        'splits_data': splits_data,
                        'split_summaries': split_summaries,
                        'typed_splits': typed_splits
                    }
                except Exception as api_error:
                    self.logger.error(f"API error fetching detailed data for {activity_name}: {api_error}")
                    detailed_data = None
                
                # Record API request
                await self.load_manager.record_request("garmin", detailed_data is not None)
                
                if detailed_data:
                    # Add detailed data to the activity
                    activity['detailed_swimming_data'] = detailed_data
                    self.logger.info(f"Successfully fetched detailed data for {activity_name}")
                else:
                    self.logger.warning(f"No detailed data found for {activity_name}")
                
                # Add small delay to respect rate limits
                import asyncio
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to fetch detailed data for {activity_name} (ID: {activity_id}): {e}")
                # Continue with other activities even if one fails
                continue
        
        return raw_data

    async def fetch_and_cache_raw_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Fetch raw data from Garmin API and cache it."""
        # Check cache first
        cached_data = self._load_from_cache(target_date)
        if cached_data is not None:
            return cached_data
        
        try:
            # Check rate limits before making API calls
            if not await self.load_manager.can_make_request("garmin"):
                self.logger.warning("Rate limit reached, waiting...")
                await self.load_manager.wait_for_rate_limit("garmin")
            
            # Fetch raw data from API
            self.logger.info(f"Fetching raw data from API for {target_date}")
            raw_data = await self.garmin_client._fetch_raw_data(target_date)
            
            # Record API request
            await self.load_manager.record_request("garmin", raw_data is not None)
            
            if raw_data:
                # Fetch detailed swimming data for all swimming activities
                enhanced_raw_data = await self._fetch_detailed_swimming_data(raw_data)
                
                # Save enhanced data to cache
                self._save_to_cache(target_date, enhanced_raw_data)
                self.logger.info(f"Successfully fetched and cached enhanced raw data for {target_date}")
                return enhanced_raw_data
            else:
                self.logger.warning(f"No raw data found for {target_date}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to fetch raw data for {target_date}: {e}")
            return None
    
    async def execute_recovery_etl(self, raw_data: Dict[str, Any], target_date: date) -> JobResult:
        """Execute recovery data ETL job using cached raw data."""
        from datetime import datetime
        import time
        
        job_id = f"recovery_etl_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting recovery ETL job {job_id} for date: {target_date}")
            
            if not raw_data:
                self.logger.warning(f"No raw data available for recovery processing on {target_date}")
                return JobResult(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    records_processed=0,
                    errors=["No raw data available"]
                )
            
            # Transform: Process data using RecoveryProcessor
            self.logger.info("Transforming recovery data")
            extracted_data = self.recovery_processor.extract(raw_data, target_date)
            transformed_data = self.recovery_processor.transform(extracted_data, target_date)
            
            # Load: Store data in database
            self.logger.info("Loading recovery data to database")
            records_processed = await self.recovery_processor.load(transformed_data, self.db_manager)
            
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            self.logger.info(f"Recovery ETL job {job_id} completed successfully. Records processed: {records_processed}")
            
            return JobResult(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                records_processed=records_processed,
                errors=[]
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            self.logger.error(f"Recovery ETL job {job_id} failed: {e}")
            
            return JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                records_processed=0,
                errors=[str(e)]
            )
        
    async def execute_swimming_etl(self) -> JobResult:
        """Execute swimming data ETL job."""
        try:
            self.logger.info("Starting swimming ETL execution")
            
            # Initialize processors
            processors = self._initialize_swimming_processors()
            
            # Get cached files
            cached_files = self._get_cached_files()
            if not cached_files:
                return self._create_no_files_result()
            
            # Process all cached files
            results = await self._process_cached_files(cached_files, processors)
            
            # Create final result
            return self._create_swimming_etl_result(results)
            
        except Exception as e:
            self.logger.error(f"Swimming ETL failed: {str(e)}")
            return JobResult(
                job_id="swimming_etl",
                status=JobStatus.FAILED,
                message=f"Swimming ETL failed: {str(e)}",
                records_processed=0
            )
    
    def _initialize_swimming_processors(self) -> Dict[str, Any]:
        """Initialize swimming processors."""
        from ..processing.processors.swimming_sessions_processor import SwimmingSessionsProcessor
        from ..processing.processors.swimming_intervals_processor import SwimmingIntervalsProcessor
        from ..processing.processors.swimming_laps_processor import SwimmingLapsProcessor
        
        return {
            'sessions': SwimmingSessionsProcessor(),
            'intervals': SwimmingIntervalsProcessor(),
            'laps': SwimmingLapsProcessor()
        }
    
    def _get_cached_files(self) -> List[Path]:
        """Get all cached JSON files."""
        return list(self.cache_dir.glob("*.json"))
    
    def _create_no_files_result(self) -> JobResult:
        """Create result when no cached files found."""
        self.logger.warning("No cached files found for swimming ETL")
        return JobResult(
            job_id="swimming_etl",
            status=JobStatus.COMPLETED,
            message="No cached files found",
            records_processed=0
        )
    
    async def _process_cached_files(self, cached_files: List[Path], processors: Dict[str, Any]) -> Dict[str, Any]:
        """Process all cached files and return aggregated results."""
        total_sessions = 0
        total_intervals = 0
        total_laps = 0
        processed_dates = []
        
        for cache_file in cached_files:
            try:
                result = await self._process_single_cache_file(cache_file, processors)
                if result:
                    total_sessions += result['sessions']
                    total_intervals += result['intervals']
                    total_laps += result['laps']
                    processed_dates.append(result['date'])
                    
            except Exception as e:
                self.logger.error(f"Error processing {cache_file}: {str(e)}")
                continue
        
        return {
            'sessions': total_sessions,
            'intervals': total_intervals,
            'laps': total_laps,
            'dates': processed_dates
        }
    
    async def _process_single_cache_file(self, cache_file: Path, processors: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single cached file."""
        date_str = cache_file.stem
        target_date = date.fromisoformat(date_str)
        
        self.logger.info(f"Processing swimming data for {date_str}")
        
        # Load cached data
        with open(cache_file, 'r') as f:
            raw_data = json.load(f)
        
        # Check if this file has swimming data
        if 'swimming_data' not in raw_data or not raw_data['swimming_data'].get('activities'):
            self.logger.info(f"No swimming data found in {date_str}")
            return None
        
        # Execute ETL for each processor
        sessions_count = await processors['sessions'].run(raw_data, target_date, self.db_manager)
        intervals_count = await processors['intervals'].run(raw_data, target_date, self.db_manager)
        laps_count = await processors['laps'].run(raw_data, target_date, self.db_manager)
        
        self.logger.info(f"Processed {date_str}: {sessions_count} sessions, {intervals_count} intervals, {laps_count} laps")
        
        return {
            'date': date_str,
            'sessions': sessions_count,
            'intervals': intervals_count,
            'laps': laps_count
        }
    
    def _create_swimming_etl_result(self, results: Dict[str, Any]) -> JobResult:
        """Create final swimming ETL result."""
        total_records = results['sessions'] + results['intervals'] + results['laps']
        message = f"Processed {len(results['dates'])} dates: {results['sessions']} sessions, {results['intervals']} intervals, {results['laps']} laps"
        
        self.logger.info(f"Swimming ETL completed: {message}")
        
        return JobResult(
            job_id="swimming_etl",
            status=JobStatus.COMPLETED,
            message=message,
            records_processed=total_records,
            metadata={
                "dates_processed": results['dates'],
                "sessions": results['sessions'],
                "intervals": results['intervals'],
                "laps": results['laps']
            }
        )
    
    async def _run_individual_processor(self, processor_class: str, target_date: Optional[date] = None) -> JobResult:
        """Run an individual processor with cached data."""
        try:
            # Dynamic import of processor class
            module_name = processor_class.lower().replace('processor', '_processor')
            # Fix for swimming processors
            if 'swimming' in module_name:
                module_name = module_name.replace('swimming', 'swimming_')
            
            if 'swimming' in module_name:
                from ..processing.processors import swimming_sessions_processor, swimming_intervals_processor, swimming_laps_processor
                module_map = {
                    'swimming_sessions_processor': swimming_sessions_processor,
                    'swimming_intervals_processor': swimming_intervals_processor,
                    'swimming_laps_processor': swimming_laps_processor
                }
            else:
                # Add other processor types here as needed
                raise ValueError(f"Unknown processor type: {processor_class}")
            
            if module_name not in module_map:
                raise ValueError(f"Module {module_name} not found in module_map")
            
            module = module_map[module_name]
            processor_class_obj = getattr(module, processor_class)
            processor = processor_class_obj()
            
            # Get cached files
            if target_date:
                # Process specific date
                cache_file = self.cache_dir / f"{target_date.isoformat()}.json"
                if not cache_file.exists():
                    return JobResult(
                        job_id=f"individual_{processor_class}",
                        status=JobStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_ms=0.0,
                        records_processed=0,
                        errors=[f"No cached data found for {target_date}"]
                    )
                cached_files = [cache_file]
            else:
                # Process all cached files
                cached_files = list(self.cache_dir.glob("*.json"))
                if not cached_files:
                    return JobResult(
                        job_id=f"individual_{processor_class}",
                        status=JobStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_ms=0.0,
                        records_processed=0,
                        errors=["No cached files found"]
                    )
            
            total_records = 0
            processed_dates = []
            
            # Process each cached file
            for cache_file in cached_files:
                try:
                    date_str = cache_file.stem
                    file_date = date.fromisoformat(date_str)
                    
                    self.logger.info(f"Processing {processor_class} for {date_str}")
                    
                    # Load cached data
                    with open(cache_file, 'r') as f:
                        raw_data = json.load(f)
                    
                    # Run processor
                    records_count = await processor.run(raw_data, file_date, self.db_manager)
                    total_records += records_count
                    processed_dates.append(date_str)
                    
                    self.logger.info(f"Processed {date_str}: {records_count} records")
                    
                except Exception as e:
                    self.logger.error(f"Error processing {cache_file} with {processor_class}: {str(e)}")
                    continue
            
            message = f"Processed {processor_class} for {len(processed_dates)} dates: {total_records} records"
            self.logger.info(message)
            
            return JobResult(
                job_id=f"individual_{processor_class}",
                status=JobStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=total_records,
                errors=[],
                metadata={
                    "processor": processor_class,
                    "dates_processed": processed_dates,
                    "target_date": target_date.isoformat() if target_date else None,
                    "message": message
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to run individual processor {processor_class}: {str(e)}")
            return JobResult(
                job_id=f"individual_{processor_class}",
                status=JobStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=0,
                errors=[f"Individual processor failed: {str(e)}"]
            )
        
    async def execute_daily_summary_etl(self) -> JobResult:
        """Execute daily summary ETL job."""
        # TODO: Implement daily summary ETL execution
        pass
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        # TODO: Implement health check
        pass
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        # TODO: Implement system status
        pass
