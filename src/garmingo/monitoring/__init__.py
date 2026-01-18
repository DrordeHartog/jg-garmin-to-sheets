"""
Monitoring and logging infrastructure for ETL pipeline.

This module provides structured logging, metrics collection, and Discord notifications
for the Garmin health data ETL pipeline.
"""

# from ..shared.logging_config import StructuredLogger, LogEntry  # TODO: These classes don't exist yet
from .discord_notifier import DiscordNotifier
from .metrics_collector import MetricsCollector

__all__ = [
    # 'StructuredLogger',
    # 'LogEntry',
    'DiscordNotifier',
    'MetricsCollector'
]
