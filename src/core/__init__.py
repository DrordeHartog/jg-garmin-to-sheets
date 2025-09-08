"""
Core module for data fetching and basic models.

This module handles:
- Garmin API client
- Data models and structures
- Credential management
"""

# Import main classes for easy access
from .garmin_client import GarminClient
from .models import (
    SleepMetrics, 
    HealthMetrics, 
    RecoveryMetrics, 
    SwimmingMetrics, 
    DailyMetrics,
    SwimmingSession,
    SwimmingInterval,
    SwimmingLap,
    SwimmingLength
)
from .bitwarden_client import BitwardenClient

# Define what gets imported with "from src.core import *"
__all__ = [
    'GarminClient',
    'SleepMetrics',
    'HealthMetrics', 
    'RecoveryMetrics',
    'SwimmingMetrics', 
    'DailyMetrics',
    'SwimmingSession',
    'SwimmingInterval',
    'SwimmingLap',
    'SwimmingLength',
    'BitwardenClient'
]