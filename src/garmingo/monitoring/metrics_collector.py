"""
Metrics collection and aggregation for ETL pipeline.

Provides methods to collect, store, and query metrics for monitoring and analysis.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class JobMetrics:
    """Job execution metrics."""
    job_id: str
    job_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    records_processed: Optional[int]
    error_message: Optional[str]

@dataclass
class APIMetrics:
    """API request metrics."""
    service: str
    endpoint: str
    status_code: int
    duration_ms: float
    timestamp: datetime
    rate_limit_remaining: Optional[int]
    rate_limit_reset: Optional[datetime]

@dataclass
class SystemMetrics:
    """System performance metrics."""
    metric_name: str
    metric_value: float
    timestamp: datetime
    tags: Optional[Dict[str, str]]

class MetricsCollector:
    """Collects and aggregates metrics for ETL pipeline monitoring."""
    
    def __init__(self, metrics_db: str = "data/metrics.db"):
        self.metrics_db = metrics_db
        
    def get_job_metrics(self, hours: int = 24) -> List[JobMetrics]:
        """Get job metrics for the last N hours."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.metrics_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT job_id, job_type, status, timestamp as start_time,
                       duration_ms, records_processed, error_message
                FROM job_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since,))
            
            metrics = []
            for row in cursor.fetchall():
                start_time = datetime.fromisoformat(row['start_time'])
                end_time = start_time + timedelta(milliseconds=row['duration_ms']) if row['duration_ms'] else None
                
                metrics.append(JobMetrics(
                    job_id=row['job_id'],
                    job_type=row['job_type'],
                    status=row['status'],
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=row['duration_ms'],
                    records_processed=row['records_processed'],
                    error_message=row['error_message']
                ))
                
            return metrics
            
    def get_api_metrics(self, service: str = None, hours: int = 24) -> List[APIMetrics]:
        """Get API metrics for the last N hours, optionally filtered by service."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.metrics_db) as conn:
            conn.row_factory = sqlite3.Row
            
            if service:
                cursor = conn.execute("""
                    SELECT service, endpoint, status_code, duration_ms, timestamp,
                           rate_limit_remaining, rate_limit_reset
                    FROM api_metrics
                    WHERE timestamp >= ? AND service = ?
                    ORDER BY timestamp DESC
                """, (since, service))
            else:
                cursor = conn.execute("""
                    SELECT service, endpoint, status_code, duration_ms, timestamp,
                           rate_limit_remaining, rate_limit_reset
                    FROM api_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (since,))
            
            metrics = []
            for row in cursor.fetchall():
                rate_limit_reset = None
                if row['rate_limit_reset']:
                    rate_limit_reset = datetime.fromisoformat(row['rate_limit_reset'])
                    
                metrics.append(APIMetrics(
                    service=row['service'],
                    endpoint=row['endpoint'],
                    status_code=row['status_code'],
                    duration_ms=row['duration_ms'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    rate_limit_remaining=row['rate_limit_remaining'],
                    rate_limit_reset=rate_limit_reset
                ))
                
            return metrics
            
    def get_system_metrics(self, metric_name: str = None, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics for the last N hours, optionally filtered by metric name."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.metrics_db) as conn:
            conn.row_factory = sqlite3.Row
            
            if metric_name:
                cursor = conn.execute("""
                    SELECT metric_name, metric_value, timestamp, tags
                    FROM system_metrics
                    WHERE timestamp >= ? AND metric_name = ?
                    ORDER BY timestamp DESC
                """, (since, metric_name))
            else:
                cursor = conn.execute("""
                    SELECT metric_name, metric_value, timestamp, tags
                    FROM system_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (since,))
            
            metrics = []
            for row in cursor.fetchall():
                tags = json.loads(row['tags']) if row['tags'] else None
                
                metrics.append(SystemMetrics(
                    metric_name=row['metric_name'],
                    metric_value=row['metric_value'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    tags=tags
                ))
                
            return metrics
            
    def get_job_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for jobs in the last N hours."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.metrics_db) as conn:
            # Overall job statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_jobs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_jobs,
                    AVG(duration_ms) as avg_duration_ms,
                    SUM(records_processed) as total_records
                FROM job_metrics
                WHERE timestamp >= ?
            """, (since,))
            
            row = cursor.fetchone()
            summary = {
                'total_jobs': row[0] or 0,
                'successful_jobs': row[1] or 0,
                'failed_jobs': row[2] or 0,
                'avg_duration_ms': row[3] or 0,
                'total_records': row[4] or 0
            }
            
            # Success rate
            if summary['total_jobs'] > 0:
                summary['success_rate'] = (summary['successful_jobs'] / summary['total_jobs']) * 100
            else:
                summary['success_rate'] = 0
                
            # Job type breakdown
            cursor = conn.execute("""
                SELECT job_type, COUNT(*) as count, 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                FROM job_metrics
                WHERE timestamp >= ?
                GROUP BY job_type
            """, (since,))
            
            job_types = {}
            for row in cursor.fetchall():
                job_types[row[0]] = {
                    'total': row[1],
                    'successful': row[2],
                    'success_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
                }
                
            summary['job_types'] = job_types
            
            return summary
            
    def get_api_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for API calls in the last N hours."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.metrics_db) as conn:
            # Overall API statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(duration_ms) as avg_duration_ms,
                    MAX(duration_ms) as max_duration_ms,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_requests
                FROM api_metrics
                WHERE timestamp >= ?
            """, (since,))
            
            row = cursor.fetchone()
            summary = {
                'total_requests': row[0] or 0,
                'avg_duration_ms': row[1] or 0,
                'max_duration_ms': row[2] or 0,
                'error_requests': row[3] or 0
            }
            
            # Error rate
            if summary['total_requests'] > 0:
                summary['error_rate'] = (summary['error_requests'] / summary['total_requests']) * 100
            else:
                summary['error_rate'] = 0
                
            # Service breakdown
            cursor = conn.execute("""
                SELECT service, COUNT(*) as count, AVG(duration_ms) as avg_duration
                FROM api_metrics
                WHERE timestamp >= ?
                GROUP BY service
            """, (since,))
            
            services = {}
            for row in cursor.fetchall():
                services[row[0]] = {
                    'requests': row[1],
                    'avg_duration_ms': row[2] or 0
                }
                
            summary['services'] = services
            
            return summary
            
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        
        with sqlite3.connect(self.metrics_db) as conn:
            # Recent job failures
            cursor = conn.execute("""
                SELECT COUNT(*) as recent_failures
                FROM job_metrics
                WHERE timestamp >= ? AND status = 'failed'
            """, (last_hour,))
            
            recent_failures = cursor.fetchone()[0] or 0
            
            # Recent API errors
            cursor = conn.execute("""
                SELECT COUNT(*) as recent_api_errors
                FROM api_metrics
                WHERE timestamp >= ? AND status_code >= 400
            """, (last_hour,))
            
            recent_api_errors = cursor.fetchone()[0] or 0
            
            # Last successful job
            cursor = conn.execute("""
                SELECT MAX(timestamp) as last_success
                FROM job_metrics
                WHERE status = 'completed'
            """)
            
            last_success = cursor.fetchone()[0]
            if last_success:
                last_success = datetime.fromisoformat(last_success)
                time_since_success = (now - last_success).total_seconds() / 3600  # hours
            else:
                time_since_success = float('inf')
                
            # Determine health status
            if recent_failures > 5 or recent_api_errors > 10 or time_since_success > 24:
                health_status = "critical"
            elif recent_failures > 2 or recent_api_errors > 5 or time_since_success > 12:
                health_status = "warning"
            else:
                health_status = "healthy"
                
            return {
                'status': health_status,
                'recent_failures': recent_failures,
                'recent_api_errors': recent_api_errors,
                'time_since_last_success_hours': time_since_success,
                'last_success': last_success.isoformat() if last_success else None
            }
