"""
Table processors for the ETL pipeline.

Each processor handles extract, transform, and load operations for a specific database table.
"""

from .base_processor import BaseTableProcessor
from .daily_summary_processor import DailySummaryProcessor
from .recovery_processor import RecoveryProcessor
from .activities_processor import ActivitiesProcessor
from .swimming_sessions_processor import SwimmingSessionsProcessor
from .swimming_intervals_processor import SwimmingIntervalsProcessor
from .swimming_laps_processor import SwimmingLapsProcessor
from .swimming_lengths_processor import SwimmingLengthsProcessor

__all__ = [
    'BaseTableProcessor',
    'DailySummaryProcessor',
    'RecoveryProcessor', 
    'ActivitiesProcessor',
    'SwimmingSessionsProcessor',
    'SwimmingIntervalsProcessor',
    'SwimmingLapsProcessor',
    'SwimmingLengthsProcessor'
]
