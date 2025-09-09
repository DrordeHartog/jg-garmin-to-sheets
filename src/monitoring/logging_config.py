"""
Structured logging configuration for ETL pipeline.

Provides JSON-based structured logging with file output and metrics collection.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from contextlib import contextmanager

@dataclass
class LogEntry:
    """Structured log entry for consistent logging."""
    timestamp: datetime
    level: str
    service: str
    job_id: Optional[str]
    message: str
    metadata: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[str] = None

class StructuredLogger:
    """Logger that writes structured JSON logs and metrics to SQLite."""
    
    def __init__(self, log_dir: str = "logs", metrics_db: str = "data/metrics.db"):
        self.log_dir = Path(log_dir)
        self.metrics_db = metrics_db
        self.setup_directories()
        self.setup_metrics_db()
        self.setup_file_logging()
        
    def setup_directories(self):
        """Create necessary directories."""
        self.log_dir.mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
    def setup_metrics_db(self):
        """Initialize metrics database with schema."""
        with sqlite3.connect(self.metrics_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    job_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration_ms REAL,
                    records_processed INTEGER,
                    error_message TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    service TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status_code INTEGER,
                    duration_ms REAL,
                    rate_limit_remaining INTEGER,
                    rate_limit_reset DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    tags TEXT
                )
            """)
            
            # Create indexes for Grafana queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_metrics_timestamp ON job_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_metrics_job_type ON job_metrics(job_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_metrics_timestamp ON api_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_metrics_service ON api_metrics(service)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)")
            
    def setup_file_logging(self):
        """Setup file-based logging."""
        # Application logs
        app_handler = logging.FileHandler(self.log_dir / "application.log")
        app_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Error logs
        error_handler = logging.FileHandler(self.log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)
        
    def log_job_start(self, job_id: str, job_type: str, **metadata):
        """Log job start with structured data."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            service="etl_orchestrator",
            job_id=job_id,
            message=f"Job started: {job_type}",
            metadata=metadata
        )
        
        self._write_log_entry(entry)
        self._store_job_metric(job_id, job_type, "started", metadata=metadata)
        
    def log_job_completion(self, job_id: str, duration_ms: float, 
                          records_processed: int, **metadata):
        """Log job completion with metrics."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            service="etl_orchestrator",
            job_id=job_id,
            message=f"Job completed: {records_processed} records processed",
            duration_ms=duration_ms,
            metadata=metadata
        )
        
        self._write_log_entry(entry)
        self._store_job_metric(
            job_id, 
            metadata.get('job_type', 'unknown'), 
            "completed", 
            duration_ms=duration_ms,
            records_processed=records_processed,
            metadata=metadata
        )
        
    def log_job_failure(self, job_id: str, error: Exception, **metadata):
        """Log job failure with error details."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="ERROR",
            service="etl_orchestrator",
            job_id=job_id,
            message=f"Job failed: {str(error)}",
            error=str(error),
            metadata=metadata
        )
        
        self._write_log_entry(entry)
        self._store_job_metric(
            job_id,
            metadata.get('job_type', 'unknown'),
            "failed",
            error_message=str(error),
            metadata=metadata
        )
        
    def log_api_request(self, service: str, endpoint: str, 
                       status_code: int, duration_ms: float,
                       rate_limit_remaining: Optional[int] = None,
                       rate_limit_reset: Optional[datetime] = None):
        """Log API request metrics."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            service=service,
            job_id=None,
            message=f"API request: {endpoint} - {status_code}",
            metadata={
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "rate_limit_remaining": rate_limit_remaining,
                "rate_limit_reset": rate_limit_reset.isoformat() if rate_limit_reset else None
            }
        )
        
        self._write_log_entry(entry)
        self._store_api_metric(
            service, endpoint, status_code, duration_ms,
            rate_limit_remaining, rate_limit_reset
        )
        
    def log_system_metric(self, metric_name: str, metric_value: float, 
                         tags: Optional[Dict[str, str]] = None):
        """Log system metrics."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            service="system",
            job_id=None,
            message=f"System metric: {metric_name} = {metric_value}",
            metadata={"metric_name": metric_name, "metric_value": metric_value, "tags": tags}
        )
        
        self._write_log_entry(entry)
        self._store_system_metric(metric_name, metric_value, tags)
        
    def _write_log_entry(self, entry: LogEntry):
        """Write structured log entry to file."""
        log_file = self.log_dir / f"{entry.service}.log"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
            
    def _store_job_metric(self, job_id: str, job_type: str, status: str,
                         duration_ms: Optional[float] = None,
                         records_processed: Optional[int] = None,
                         error_message: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """Store job metrics in database."""
        with sqlite3.connect(self.metrics_db) as conn:
            conn.execute("""
                INSERT INTO job_metrics 
                (job_id, job_type, status, duration_ms, records_processed, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, job_type, status, duration_ms, 
                records_processed, error_message,
                json.dumps(metadata) if metadata else None
            ))
            
    def _store_api_metric(self, service: str, endpoint: str, status_code: int,
                         duration_ms: float, rate_limit_remaining: Optional[int],
                         rate_limit_reset: Optional[datetime]):
        """Store API metrics in database."""
        with sqlite3.connect(self.metrics_db) as conn:
            conn.execute("""
                INSERT INTO api_metrics 
                (service, endpoint, status_code, duration_ms, rate_limit_remaining, rate_limit_reset)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                service, endpoint, status_code, duration_ms,
                rate_limit_remaining, rate_limit_reset
            ))
            
    def _store_system_metric(self, metric_name: str, metric_value: float,
                            tags: Optional[Dict[str, str]]):
        """Store system metrics in database."""
        with sqlite3.connect(self.metrics_db) as conn:
            conn.execute("""
                INSERT INTO system_metrics (metric_name, metric_value, tags)
                VALUES (?, ?, ?)
            """, (
                metric_name, metric_value,
                json.dumps(tags) if tags else None
            ))
            
    @contextmanager
    def job_context(self, job_id: str, job_type: str, **metadata):
        """Context manager for job logging."""
        start_time = datetime.now()
        self.log_job_start(job_id, job_type, **metadata)
        
        try:
            yield
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.log_job_completion(job_id, duration_ms, 0, job_type=job_type, **metadata)
        except Exception as e:
            self.log_job_failure(job_id, e, job_type=job_type, **metadata)
            raise
