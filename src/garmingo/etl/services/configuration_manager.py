"""
Configuration Manager service.

Handles all configuration-related operations including metrics, user preferences,
and system settings.
"""

import asyncio
from typing import Optional, List, Mapping, Any, Dict
import logging

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages all configuration operations for the ETL system."""
    
    def __init__(self, db_client):
        """
        Initialize configuration manager.
        
        Args:
            db_client: DatabaseClient instance for database operations
        """
        self.db_client = db_client
        logger.info("ConfigurationManager initialized")
    
    # Metrics Configuration Methods
    
    async def add_metric(self, metric_name: str, source: str, api_endpoint: str, 
                        api_field_path: str, data_type: str, unit: str = None, 
                        description: str = None) -> int:
        """Add a new metric to the configuration table."""
        query = """
        INSERT INTO metric_config 
        (metric_name, source, api_endpoint, api_field_path, data_type, unit, description, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """
        params = (metric_name, source, api_endpoint, api_field_path, data_type, unit, description)
        result = await self.db_client.execute_query(query, params)
        logger.info(f"Added metric: {metric_name} from {source}")
        return result.lastrowid
    
    async def add_metrics(self, metrics: List[dict]) -> List[int]:
        """Add multiple metrics to the configuration table."""
        if not metrics:
            return []
        
        # Validate all metrics first
        for metric in metrics:
            if not self._validate_metric_data(metric):
                raise ValueError(f"Invalid metric data: {metric}")
        
        query = """
        INSERT INTO metric_config 
        (metric_name, source, api_endpoint, api_field_path, data_type, unit, description, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """
        rows = [(m['metric_name'], m['source'], m['api_endpoint'], m['api_field_path'], 
                 m['data_type'], m.get('unit'), m.get('description')) for m in metrics]
        
        result = await self.db_client.execute_many(query, rows)
        logger.info(f"Added {len(metrics)} metrics to configuration")
        return result
    
    async def get_active_metrics(self, source: str = None) -> List[Mapping[str, Any]]:
        """Get all active metrics, optionally filtered by source."""
        if source:
            query = "SELECT * FROM metric_config WHERE source = ? AND is_active = 1 ORDER BY metric_name"
            params = (source,)
        else:
            query = "SELECT * FROM metric_config WHERE is_active = 1 ORDER BY metric_name"
            params = ()
        
        metrics = await self.db_client.fetch_all(query, params)
        logger.debug(f"Retrieved {len(metrics)} active metrics" + (f" for source {source}" if source else ""))
        return metrics
    
    async def get_metric_by_id(self, metric_id: int) -> Optional[Mapping[str, Any]]:
        """Get a specific metric by ID."""
        query = "SELECT * FROM metric_config WHERE id = ? AND is_active = 1"
        metric = await self.db_client.fetch_one(query, (metric_id,))
        if metric:
            logger.debug(f"Retrieved metric {metric_id}: {metric['metric_name']}")
        return metric
    
    async def get_metric_by_name(self, metric_name: str, source: str = None) -> Optional[Mapping[str, Any]]:
        """Get a metric by name, optionally filtered by source."""
        if source:
            query = "SELECT * FROM metric_config WHERE metric_name = ? AND source = ? AND is_active = 1"
            params = (metric_name, source)
        else:
            query = "SELECT * FROM metric_config WHERE metric_name = ? AND is_active = 1"
            params = (metric_name,)
        
        metric = await self.db_client.fetch_one(query, params)
        if metric:
            logger.debug(f"Retrieved metric by name: {metric_name}")
        return metric
    
    async def disable_metric(self, metric_id: int) -> bool:
        """Disable a metric by setting is_active = 0."""
        query = "UPDATE metric_config SET is_active = 0 WHERE id = ?"
        result = await self.db_client.execute_query(query, (metric_id,))
        success = result.rowcount > 0
        if success:
            logger.info(f"Disabled metric {metric_id}")
        else:
            logger.warning(f"Failed to disable metric {metric_id} - not found")
        return success
    
    async def enable_metric(self, metric_id: int) -> bool:
        """Enable a metric by setting is_active = 1."""
        query = "UPDATE metric_config SET is_active = 1 WHERE id = ?"
        result = await self.db_client.execute_query(query, (metric_id,))
        success = result.rowcount > 0
        if success:
            logger.info(f"Enabled metric {metric_id}")
        else:
            logger.warning(f"Failed to enable metric {metric_id} - not found")
        return success
    
    async def get_metrics_by_source(self, source: str) -> List[Mapping[str, Any]]:
        """Get all metrics (active and inactive) for a specific source."""
        query = "SELECT * FROM metric_config WHERE source = ? ORDER BY metric_name"
        metrics = await self.db_client.fetch_all(query, (source,))
        logger.debug(f"Retrieved {len(metrics)} metrics for source {source}")
        return metrics
    
    # ETL Job Configuration Methods
    
    async def add_etl_job(self, job_id: str, job_name: str, job_type: str, 
                         processor_class: str, job_module: str, description: str = None,
                         schedule: str = None, priority: int = 1, retry_count: int = 3,
                         timeout_seconds: int = 1800, config_json: str = None) -> int:
        """Add a new ETL job to the configuration table."""
        query = """
        INSERT INTO etl_job_config 
        (job_id, job_name, job_type, processor_class, job_module, description, 
         schedule, priority, retry_count, timeout_seconds, config_json, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        params = (job_id, job_name, job_type, processor_class, job_module, description,
                 schedule, priority, retry_count, timeout_seconds, config_json)
        result = await self.db_client.execute_query(query, params)
        logger.info(f"Added ETL job: {job_name} ({job_id})")
        return result.lastrowid
    
    async def get_active_etl_jobs(self, job_type: str = None) -> List[Mapping[str, Any]]:
        """Get all active ETL jobs, optionally filtered by job type."""
        if job_type:
            query = """
            SELECT job_id, job_name, job_type, processor_class, job_module, description,
                   schedule, priority, retry_count, timeout_seconds, config_json
            FROM etl_job_config 
            WHERE is_active = 1 AND job_type = ?
            ORDER BY priority, job_id
            """
            params = (job_type,)
        else:
            query = """
            SELECT job_id, job_name, job_type, processor_class, job_module, description,
                   schedule, priority, retry_count, timeout_seconds, config_json
            FROM etl_job_config 
            WHERE is_active = 1
            ORDER BY priority, job_id
            """
            params = ()
        
        jobs = await self.db_client.fetch_all(query, params)
        logger.debug(f"Retrieved {len(jobs)} active ETL jobs" + (f" of type {job_type}" if job_type else ""))
        return jobs
    
    async def get_etl_job_by_id(self, job_id: str) -> Optional[Mapping[str, Any]]:
        """Get a specific ETL job by job_id."""
        query = """
        SELECT job_id, job_name, job_type, processor_class, job_module, description,
               schedule, priority, retry_count, timeout_seconds, config_json, is_active
        FROM etl_job_config 
        WHERE job_id = ?
        """
        job = await self.db_client.fetch_one(query, (job_id,))
        if job:
            logger.debug(f"Retrieved ETL job: {job['job_name']} ({job_id})")
        return job
    
    async def update_etl_job_schedule(self, job_id: str, schedule: str) -> bool:
        """Update ETL job schedule."""
        query = "UPDATE etl_job_config SET schedule = ?, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?"
        result = await self.db_client.execute_query(query, (schedule, job_id))
        success = result.rowcount > 0
        if success:
            logger.info(f"Updated schedule for ETL job {job_id}: {schedule}")
        else:
            logger.warning(f"Failed to update schedule for ETL job {job_id} - not found")
        return success
    
    async def update_etl_job_priority(self, job_id: str, priority: int) -> bool:
        """Update ETL job priority."""
        query = "UPDATE etl_job_config SET priority = ?, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?"
        result = await self.db_client.execute_query(query, (priority, job_id))
        success = result.rowcount > 0
        if success:
            logger.info(f"Updated priority for ETL job {job_id}: {priority}")
        return success
    
    async def update_etl_job_config(self, job_id: str, config_json: str) -> bool:
        """Update ETL job configuration JSON."""
        query = "UPDATE etl_job_config SET config_json = ?, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?"
        result = await self.db_client.execute_query(query, (config_json, job_id))
        success = result.rowcount > 0
        if success:
            logger.info(f"Updated config for ETL job {job_id}")
        return success
    
    async def disable_etl_job(self, job_id: str) -> bool:
        """Disable an ETL job by setting is_active = 0."""
        query = "UPDATE etl_job_config SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?"
        result = await self.db_client.execute_query(query, (job_id,))
        success = result.rowcount > 0
        if success:
            logger.info(f"Disabled ETL job {job_id}")
        return success
    
    async def enable_etl_job(self, job_id: str) -> bool:
        """Enable an ETL job by setting is_active = 1."""
        query = "UPDATE etl_job_config SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?"
        result = await self.db_client.execute_query(query, (job_id,))
        success = result.rowcount > 0
        if success:
            logger.info(f"Enabled ETL job {job_id}")
        return success
    
    async def get_etl_jobs_by_type(self, job_type: str) -> List[Mapping[str, Any]]:
        """Get all ETL jobs (active and inactive) for a specific job type."""
        query = """
        SELECT job_id, job_name, job_type, processor_class, job_module, description,
               schedule, priority, retry_count, timeout_seconds, config_json, is_active
        FROM etl_job_config 
        WHERE job_type = ?
        ORDER BY priority, job_id
        """
        jobs = await self.db_client.fetch_all(query, (job_type,))
        logger.debug(f"Retrieved {len(jobs)} ETL jobs of type {job_type}")
        return jobs
    
    # System Settings Configuration Methods
    
    async def add_system_setting(self, key: str, value: str, description: str = None) -> int:
        """Add or update a system setting."""
        # TODO: Implement when system_settings table is created
        raise NotImplementedError("System settings table not yet implemented")
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """Get all system settings."""
        # TODO: Implement when system_settings table is created
        raise NotImplementedError("System settings table not yet implemented")
    
    async def update_system_setting(self, key: str, value: str) -> bool:
        """Update a system setting value."""
        # TODO: Implement when system_settings table is created
        raise NotImplementedError("System settings table not yet implemented")
    
    # User Preferences Configuration Methods
    
    async def add_user_preference(self, user_id: int, key: str, value: str) -> int:
        """Add or update a user preference."""
        # TODO: Implement when user_preferences table is created
        raise NotImplementedError("User preferences table not yet implemented")
    
    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get all preferences for a user."""
        # TODO: Implement when user_preferences table is created
        raise NotImplementedError("User preferences table not yet implemented")
    
    # Private Helper Methods
    
    def _validate_metric_data(self, metric_data: dict) -> bool:
        """Validate that metric data contains required fields."""
        required_fields = ['metric_name', 'source', 'api_endpoint', 'api_field_path', 'data_type']
        return all(field in metric_data for field in required_fields)
    
    def _extract_field_value(self, data: dict, field_path: str) -> Any:
        """Extract value using dot notation path like 'hrvSummary.weeklyAvg'."""
        keys = field_path.split('.')
        value = data
        for key in keys:
            value = value.get(key)
            if value is None:
                break
        return value

