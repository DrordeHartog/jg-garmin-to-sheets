"""
ETL (Extract, Transform, Load) pipeline for Garmin health data.

This module provides a complete ETL pipeline with orchestration, processing,
and utilities for Garmin health data.
"""

# Orchestration layer
from .orchestration import (
    ETLOrchestrator,
    LoadManager,
    JobManager,
    WebhookAPI,
    OrchestratorConfig,
    JobConfig,
    JobResult,
    JobStatus
)

# Processing layer
from .processing import (
    DataProcessor,
    BaseTableProcessor,
    DailySummaryProcessor,
    RecoveryProcessor,
    ActivitiesProcessor,
    SwimmingSessionsProcessor,
    SwimmingIntervalsProcessor,
    SwimmingLapsProcessor,
    SwimmingLengthsProcessor
)

# Utils layer
from .utils import (
    validate_job_config,
    validate_date_range,
    transform_garmin_data,
    clean_data
)

__all__ = [
    # Orchestration
    'ETLOrchestrator',
    'LoadManager',
    'JobManager',
    'WebhookAPI',
    'OrchestratorConfig',
    'JobConfig',
    'JobResult',
    'JobStatus',
    # Processing
    'DataProcessor',
    'BaseTableProcessor',
    'DailySummaryProcessor',
    'RecoveryProcessor',
    'ActivitiesProcessor',
    'SwimmingSessionsProcessor',
    'SwimmingIntervalsProcessor',
    'SwimmingLapsProcessor',
    'SwimmingLengthsProcessor',
    # Utils
    'validate_job_config',
    'validate_date_range',
    'transform_garmin_data',
    'clean_data'
]
