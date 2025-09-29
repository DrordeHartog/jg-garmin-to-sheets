"""
Swimming Analytics Dashboard Package

A comprehensive web-based dashboard for analyzing swimming performance data
from Garmin Connect using Streamlit and Plotly.
"""

__version__ = "1.0.0"
__author__ = "GarminGo Team"

from .swim_dashboard import (
    load_swim_data,
    calculate_swim_metrics,
    create_performance_overview,
    create_distance_trend_chart,
    create_pace_analysis,
    create_heart_rate_analysis,
    create_swolf_analysis,
    create_stroke_analysis,
    create_activity_summary
)

__all__ = [
    "load_swim_data",
    "calculate_swim_metrics", 
    "create_performance_overview",
    "create_distance_trend_chart",
    "create_pace_analysis",
    "create_heart_rate_analysis",
    "create_swolf_analysis",
    "create_stroke_analysis",
    "create_activity_summary"
]
