"""
ETL Orchestrator.

Coordinates and executes ETL jobs using job configuration table.
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
import logging
import importlib
from pathlib import Path

from ..services.garmin_client import GarminClient
from ..utils.cache_manager import CacheManager
from .config import OrchestratorConfig, JobResult, JobStatus
from monitoring.discord_notifier import DiscordNotifier

logger = logging.getLogger(__name__)


class ETLOrchestrator:
    """Main orchestrator for ETL pipeline."""
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        from pathlib import Path
        
        # Use provided config or create default
        if config is None:
            config = OrchestratorConfig()
        
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.garmin_client = GarminClient()
        self.cache_manager = CacheManager(self.cache_dir)
        
        # Initialize database client for job configuration queries
        from database.database_manager import DatabaseManager
        from ..services.database_client import DatabaseClient
        db_manager = DatabaseManager(config.database_path)
        self.database_client = DatabaseClient(db_manager)
        
        # Initialize Discord notifier if configured
        self.discord_notifier = None
        if config.notifications and config.notifications.enabled and config.notifications.webhook_url:
            self.discord_notifier = DiscordNotifier(config.notifications)
            logger.info("Discord notifications enabled")
        else:
            logger.info("Discord notifications disabled")
        
        logger.info(f"ETL Orchestrator initialized with cache_dir: {self.cache_dir}")
    
    async def trigger_etl_job(self, job_id: int, target_date: Optional[date] = None) -> JobResult:
        """
        Trigger an ETL job by ID using job configuration table.
        
        Args:
            job_id: Job ID from etl_job_config table
            target_date: Optional target date for the job
            
        Returns:
            JobResult with execution status and details
        """
        try:
            # Query job config from database
            with self.database_client.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_name, processor_class, job_module, description 
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
            
            job_name, processor_class, job_module, description = job_config
            logger.info(f"Triggering job {job_id}: {job_name} - {description}")
            
            # Dynamically load and run the job
            return await self._run_job_by_config(processor_class, job_module, target_date, job_id)
                
        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {str(e)}")
            return JobResult(
                job_id=f"manual_{job_id}",
                status=JobStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=0,
                errors=[f"Job trigger failed: {str(e)}"]
            )
    
    async def trigger_multiple_etl_jobs(self, job_ids: Optional[List[int]] = None, target_date: Optional[date] = None) -> List[JobResult]:
        """
        Trigger multiple ETL jobs by ID or all active jobs.
        
        Args:
            job_ids: List of job IDs from etl_job_config table. If None, triggers all active jobs.
            target_date: Optional target date for the jobs
            
        Returns:
            List of JobResult with execution status and details for each job
        """
        try:
            # Get job IDs to execute
            if job_ids is None:
                # Get all active job IDs
                with self.database_client.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT job_id FROM etl_job_config 
                        WHERE is_active = 1 
                        ORDER BY job_id
                    """)
                    job_ids = [row[0] for row in cursor.fetchall()]
                
                if not job_ids:
                    logger.warning("No active jobs found in configuration")
                    return []
                
                logger.info(f"Triggering all {len(job_ids)} active jobs: {job_ids}")
            else:
                logger.info(f"Triggering {len(job_ids)} specified jobs: {job_ids}")
            
            # Send batch start notification for multiple jobs
            if self.discord_notifier and len(job_ids) > 1:
                job_id_strings = [str(job_id) for job_id in job_ids]
                self.discord_notifier.send_batch_start(job_id_strings, len(job_ids))
            
            # Execute all jobs
            results = []
            for job_id in job_ids:
                result = await self.trigger_etl_job(job_id, target_date)
                results.append(result)
            
            # Send batch complete notification for multiple jobs
            if self.discord_notifier and len(job_ids) > 1:
                batch_results = self._convert_results_for_notification(results)
                self.discord_notifier.send_batch_complete(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to trigger multiple jobs: {str(e)}")
            return [JobResult(
                job_id="multiple_jobs",
                status=JobStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=0,
                errors=[f"Failed to trigger multiple jobs: {str(e)}"]
            )]
    
    async def trigger_all_active_jobs(self, target_date: Optional[date] = None) -> List[JobResult]:
        """
        Trigger all active ETL jobs (convenience method).
        
        Args:
            target_date: Optional target date for the jobs
            
        Returns:
            List of JobResult with execution status and details for each job
        """
        return await self.trigger_multiple_etl_jobs(job_ids=None, target_date=target_date)
    
    def _convert_results_for_notification(self, results: List[JobResult]) -> List[Dict[str, Any]]:
        """Convert JobResult objects to dict format expected by Discord notifier."""
        batch_results = []
        for result in results:
            batch_results.append({
                'status': 'success' if result.status == JobStatus.COMPLETED else 'failed',
                'job_id': result.job_id,
                'records_processed': result.records_processed,
                'error': result.errors[0] if result.errors else None
            })
        return batch_results
    
    async def _run_job_by_config(self, processor_class: str, job_module: str, target_date: Optional[date], job_id: int) -> JobResult:
        """
        Dynamically load and run a job based on configuration.
        
        Args:
            processor_class: Class name of the job
            job_module: Module path of the job
            target_date: Target date for the job
            job_id: Job ID for logging
            
        Returns:
            JobResult with execution status
        """
        try:
            # Dynamically import the job module
            module = importlib.import_module(job_module)
            job_class_obj = getattr(module, processor_class)
            
            # Initialize job with required dependencies
            job_instance = self._initialize_job(job_class_obj, target_date)
            
            # Run the job
            start_time = datetime.now()
            result = job_instance.run()
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Convert job result to JobResult
            return JobResult(
                job_id=f"job_{job_id}",
                status=JobStatus.COMPLETED if result.get("status") == "success" else JobStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                records_processed=result.get("transformed_records", 0),
                errors=result.get("error", []) if isinstance(result.get("error"), list) else [result.get("error")] if result.get("error") else [],
                metadata=result
            )
            
        except Exception as e:
            logger.error(f"Failed to run job {processor_class} from {job_module}: {str(e)}")
            return JobResult(
                job_id=f"job_{job_id}",
                status=JobStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_ms=0.0,
                records_processed=0,
                errors=[f"Job execution failed: {str(e)}"]
            )
    
    def _initialize_job(self, job_class, target_date: Optional[date]):
        """
        Initialize a job instance with required dependencies.
        
        Args:
            job_class: Job class to initialize
            target_date: Target date for the job
            
        Returns:
            Initialized job instance
        """
        # Determine job type and initialize with appropriate dependencies
        job_name = job_class.__name__.lower()
        
        if "garmin_api_data" in job_name:
            # API to cache jobs need GarminClient and CacheManager
            return job_class(target_date, self.garmin_client, self.cache_manager)
        elif any(x in job_name for x in ["recovery", "swimming_sessions", "swimming_laps", "swimming_intervals"]):
            # Cache to raw jobs need CacheManager and DatabaseClient
            return job_class(target_date, self.cache_manager, self.database_client)
        elif "raw_to_processed" in job_name:
            # Raw to processed jobs need DatabaseClient
            return job_class(target_date, self.database_client)
        else:
            # Default initialization
            return job_class(target_date)
    
    async def authenticate_garmin(self, email: str, password: str) -> bool:
        """Authenticate with Garmin API."""
        try:
            await self.garmin_client.authenticate(email, password)
            logger.info("Garmin authentication successful")
            return True
        except Exception as e:
            logger.error(f"Garmin authentication failed: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Get status of a specific job."""
        # TODO: Implement job status retrieval from database
        return None
    
    async def list_jobs(self) -> List[JobResult]:
        """List all jobs (active and completed)."""
        # TODO: Implement jobs listing from database
        return []
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or scheduled job."""
        # TODO: Implement job cancellation
        return False
