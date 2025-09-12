"""
Main ETL orchestrator with APScheduler integration.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional, List, Dict, Any
from datetime import date
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
        
    async def trigger_etl_job(self, job_type: str, **kwargs) -> JobResult:
        """Manually trigger an ETL job."""
        # TODO: Implement manual job triggering
        pass
        
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
    
    async def fetch_and_cache_raw_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Fetch raw data from Garmin API and cache it."""
        try:
            # Check rate limits before making API calls
            if not await self.load_manager.can_make_request("garmin"):
                self.logger.warning("Rate limit reached, waiting...")
                await self.load_manager.wait_for_rate_limit("garmin")
            
            # Fetch raw data
            self.logger.info(f"Fetching raw data for {target_date}")
            raw_data = await self.garmin_client._fetch_raw_data(target_date)
            
            # Record API request
            await self.load_manager.record_request("garmin", raw_data is not None)
            
            if raw_data:
                self.logger.info(f"Successfully cached raw data for {target_date}")
                return raw_data
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
        # TODO: Implement swimming ETL execution
        pass
        
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
