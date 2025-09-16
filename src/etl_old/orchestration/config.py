"""
Configuration dataclasses for ETL orchestrator.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum

@dataclass
class RateLimit:
    """Rate limiting configuration for a service."""
    requests_per_minute: int
    requests_per_hour: int
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 300

@dataclass
class NotificationConfig:
    """Configuration for notifications."""
    discord_webhook_url: str
    enabled: bool = True
    send_job_start: bool = True
    send_job_success: bool = True
    send_job_failure: bool = True

@dataclass
class OrchestratorConfig:
    """Main configuration for ETL orchestrator."""
    database_path: str = "data/health_data.db"
    cache_dir: str = "data/cache"
    metrics_db_path: str = "data/metrics.db"
    etl_jobs_db_path: str = "data/etl_jobs.db"
    webhook_port: int = 5000
    max_concurrent_jobs: int = 3
    job_timeout: int = 3600
    rate_limits: Dict[str, RateLimit] = field(default_factory=dict)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

class JobStatus(Enum):
    """Status of an ETL job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobConfig:
    """Configuration for an ETL job."""
    job_type: str
    date_range: Optional[Tuple[date, date]] = None
    priority: int = 1
    retry_count: int = 3
    timeout: int = 1800
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JobResult:
    """Result of an ETL job execution."""
    job_id: str
    status: JobStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    records_processed: int
    errors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
