"""
Utility functions for swimming data processing.
Shared across all swimming processors.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def convert_duration_to_seconds_and_hms(duration: Optional[Any]) -> tuple[Optional[int], Optional[str]]:
    """
    Convert duration to both integer seconds and HH:MM:SS format.
    
    Args:
        duration: Duration value (could be string, float, int)
        
    Returns:
        Tuple of (seconds_int, hms_string)
    """
    if not duration:
        return None, None
    
    try:
        seconds_int = int(float(duration))
        hms_string = format_duration_hms(seconds_int)
        return seconds_int, hms_string
    except (ValueError, TypeError):
        logger.warning(f"Could not convert duration: {duration}")
        return None, None


def format_duration_hms(duration_seconds: Optional[int]) -> Optional[str]:
    """
    Convert duration in seconds to HH:MM:SS format.
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        Formatted duration string (HH:MM:SS or MM:SS)
    """
    if not duration_seconds:
        return None
    
    try:
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    except (ValueError, TypeError):
        logger.warning(f"Could not format duration: {duration_seconds}")
        return None


def calculate_pace_per_100m_hms(session_data: Dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    """
    Calculate average pace per 100m in both seconds and HH:MM:SS format.
    
    Args:
        session_data: Session data dictionary
        
    Returns:
        Tuple of (pace_seconds, pace_hms_string)
    """
    distance = session_data.get('total_distance')
    duration = session_data.get('total_duration')
    
    if not distance or not duration:
        return None, None
    
    try:
        distance_m = float(distance)
        duration_s = float(duration)
        if distance_m > 0:
            pace_seconds = (duration_s / distance_m) * 100
            pace_hms = format_duration_hms(int(pace_seconds))
            return pace_seconds, pace_hms
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    
    return None, None


def calculate_strokes_per_length(session_data: Dict[str, Any]) -> Optional[float]:
    """Calculate average strokes per length."""
    strokes = session_data.get('total_strokes')
    lengths = session_data.get('active_lengths')
    
    if not strokes or not lengths:
        return None
    
    try:
        strokes_int = int(strokes)
        lengths_int = int(lengths)
        if lengths_int > 0:
            return strokes_int / lengths_int
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    
    return None


def calculate_strokes_per_minute(session_data: Dict[str, Any]) -> Optional[float]:
    """Calculate average strokes per minute."""
    strokes = session_data.get('total_strokes')
    duration = session_data.get('total_duration')
    
    if not strokes or not duration:
        return None
    
    try:
        strokes_int = int(strokes)
        duration_min = float(duration) / 60
        if duration_min > 0:
            return strokes_int / duration_min
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    
    return None


def determine_swim_type_counts(session_data: Dict[str, Any]) -> tuple[int, int]:
    """Determine pool vs open water swim counts."""
    has_pool_length = session_data.get('pool_length') is not None
    return (1 if has_pool_length else 0, 0 if has_pool_length else 1)
