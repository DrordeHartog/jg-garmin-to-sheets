"""
Populate metrics configuration table with real Garmin API metrics.

This script analyzes the cached Garmin API data and populates the metric_config table
with all available metrics, their field paths, and metadata.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from garmingo.database.SQLiteManager import SQLiteManager
from garmingo.etl.adapters.SQLiteClient import SQLiteClient
from garmingo.etl.services.configuration_manager import ConfigurationManager
from garmingo.database.create_metrics_config_table import create_metrics_config_table


def analyze_cached_data(cache_file_path: str) -> List[Dict[str, Any]]:
    """
    Analyze cached Garmin API data to extract available metrics.
    
    Args:
        cache_file_path: Path to the cached JSON file
        
    Returns:
        List of metric configurations
    """
    with open(cache_file_path, 'r') as f:
        data = json.load(f)
    
    metrics = []
    
    # Define metric categories and their field paths
    metric_definitions = [
        # Daily Summary Metrics
        {
            "category": "daily_summary",
            "metrics": [
                {
                    "metric_name": "total_kilocalories",
                    "api_field_path": "stats.totalKilocalories",
                    "data_type": "float",
                    "unit": "kcal",
                    "description": "Total calories burned for the day"
                },
                {
                    "metric_name": "active_kilocalories",
                    "api_field_path": "stats.activeKilocalories",
                    "data_type": "float",
                    "unit": "kcal",
                    "description": "Active calories burned (excluding BMR)"
                },
                {
                    "metric_name": "total_steps",
                    "api_field_path": "stats.totalSteps",
                    "data_type": "int",
                    "unit": "steps",
                    "description": "Total steps taken for the day"
                },
                {
                    "metric_name": "total_distance_meters",
                    "api_field_path": "stats.totalDistanceMeters",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Total distance covered in meters"
                },
                {
                    "metric_name": "resting_heart_rate",
                    "api_field_path": "stats.restingHeartRate",
                    "data_type": "int",
                    "unit": "bpm",
                    "description": "Resting heart rate"
                },
                {
                    "metric_name": "min_heart_rate",
                    "api_field_path": "stats.minHeartRate",
                    "data_type": "int",
                    "unit": "bpm",
                    "description": "Minimum heart rate for the day"
                },
                {
                    "metric_name": "max_heart_rate",
                    "api_field_path": "stats.maxHeartRate",
                    "data_type": "int",
                    "unit": "bpm",
                    "description": "Maximum heart rate for the day"
                },
                {
                    "metric_name": "average_stress_level",
                    "api_field_path": "stats.averageStressLevel",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Average stress level (0-100)"
                },
                {
                    "metric_name": "max_stress_level",
                    "api_field_path": "stats.maxStressLevel",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Maximum stress level reached"
                },
                {
                    "metric_name": "stress_percentage",
                    "api_field_path": "stats.stressPercentage",
                    "data_type": "float",
                    "unit": "percentage",
                    "description": "Percentage of time in stress state"
                },
                {
                    "metric_name": "body_battery_charged_value",
                    "api_field_path": "stats.bodyBatteryChargedValue",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Body battery charged value"
                },
                {
                    "metric_name": "body_battery_drained_value",
                    "api_field_path": "stats.bodyBatteryDrainedValue",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Body battery drained value"
                },
                {
                    "metric_name": "body_battery_highest_value",
                    "api_field_path": "stats.bodyBatteryHighestValue",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Highest body battery value for the day"
                },
                {
                    "metric_name": "body_battery_lowest_value",
                    "api_field_path": "stats.bodyBatteryLowestValue",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Lowest body battery value for the day"
                },
                {
                    "metric_name": "body_battery_most_recent_value",
                    "api_field_path": "stats.bodyBatteryMostRecentValue",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Most recent body battery value"
                },
                {
                    "metric_name": "highly_active_seconds",
                    "api_field_path": "stats.highlyActiveSeconds",
                    "data_type": "int",
                    "unit": "seconds",
                    "description": "Time spent in highly active state"
                },
                {
                    "metric_name": "active_seconds",
                    "api_field_path": "stats.activeSeconds",
                    "data_type": "int",
                    "unit": "seconds",
                    "description": "Time spent in active state"
                },
                {
                    "metric_name": "sedentary_seconds",
                    "api_field_path": "stats.sedentarySeconds",
                    "data_type": "int",
                    "unit": "seconds",
                    "description": "Time spent in sedentary state"
                },
                {
                    "metric_name": "sleeping_seconds",
                    "api_field_path": "stats.sleepingSeconds",
                    "data_type": "int",
                    "unit": "seconds",
                    "description": "Time spent sleeping"
                },
                {
                    "metric_name": "moderate_intensity_minutes",
                    "api_field_path": "stats.moderateIntensityMinutes",
                    "data_type": "int",
                    "unit": "minutes",
                    "description": "Minutes of moderate intensity activity"
                },
                {
                    "metric_name": "vigorous_intensity_minutes",
                    "api_field_path": "stats.vigorousIntensityMinutes",
                    "data_type": "int",
                    "unit": "minutes",
                    "description": "Minutes of vigorous intensity activity"
                }
            ]
        },
        
        # HRV Metrics
        {
            "category": "hrv",
            "metrics": [
                {
                    "metric_name": "hrv_weekly_avg",
                    "api_field_path": "hrv_payload.hrvSummary.weeklyAvg",
                    "data_type": "int",
                    "unit": "ms",
                    "description": "Weekly average HRV"
                },
                {
                    "metric_name": "hrv_last_night_avg",
                    "api_field_path": "hrv_payload.hrvSummary.lastNightAvg",
                    "data_type": "int",
                    "unit": "ms",
                    "description": "Last night's average HRV"
                },
                {
                    "metric_name": "hrv_last_night_5min_high",
                    "api_field_path": "hrv_payload.hrvSummary.lastNight5MinHigh",
                    "data_type": "int",
                    "unit": "ms",
                    "description": "Last night's 5-minute high HRV"
                },
                {
                    "metric_name": "hrv_baseline",
                    "api_field_path": "hrv_payload.hrvSummary.baseline",
                    "data_type": "int",
                    "unit": "ms",
                    "description": "HRV baseline value"
                }
            ]
        },
        
        # Training Status Metrics
        {
            "category": "training",
            "metrics": [
                {
                    "metric_name": "training_status",
                    "api_field_path": "training_status.trainingStatus",
                    "data_type": "int",
                    "unit": "status_code",
                    "description": "Training status code"
                },
                {
                    "metric_name": "training_status_feedback",
                    "api_field_path": "training_status.trainingStatusFeedbackPhrase",
                    "data_type": "string",
                    "unit": "text",
                    "description": "Training status feedback phrase"
                },
                {
                    "metric_name": "acute_training_load",
                    "api_field_path": "training_status.acuteTrainingLoadDTO.acwrPercent",
                    "data_type": "int",
                    "unit": "percentage",
                    "description": "Acute training load percentage"
                },
                {
                    "metric_name": "acwr_status",
                    "api_field_path": "training_status.acuteTrainingLoadDTO.acwrStatus",
                    "data_type": "string",
                    "unit": "status",
                    "description": "ACWR (Acute:Chronic Workload Ratio) status"
                }
            ]
        },
        
        # Swimming Activity Metrics
        {
            "category": "swimming_activity",
            "metrics": [
                {
                    "metric_name": "swimming_duration",
                    "api_field_path": "activities.0.duration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Total swimming session duration"
                },
                {
                    "metric_name": "swimming_elapsed_duration",
                    "api_field_path": "activities.0.elapsedDuration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Elapsed swimming session duration"
                },
                {
                    "metric_name": "swimming_moving_duration",
                    "api_field_path": "activities.0.movingDuration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Moving time during swimming session"
                },
                {
                    "metric_name": "swimming_average_speed",
                    "api_field_path": "activities.0.averageSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Average swimming speed"
                },
                {
                    "metric_name": "swimming_max_speed",
                    "api_field_path": "activities.0.maxSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Maximum swimming speed"
                },
                {
                    "metric_name": "swimming_strokes",
                    "api_field_path": "activities.0.strokes",
                    "data_type": "float",
                    "unit": "strokes",
                    "description": "Total number of strokes"
                },
                {
                    "metric_name": "swimming_avg_stroke_distance",
                    "api_field_path": "activities.0.avgStrokeDistance",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Average distance per stroke"
                },
                {
                    "metric_name": "swimming_avg_strokes",
                    "api_field_path": "activities.0.avgStrokes",
                    "data_type": "float",
                    "unit": "strokes",
                    "description": "Average strokes per lap"
                },
                {
                    "metric_name": "swimming_lap_count",
                    "api_field_path": "activities.0.lapCount",
                    "data_type": "int",
                    "unit": "laps",
                    "description": "Total number of laps"
                },
                {
                    "metric_name": "swimming_training_effect",
                    "api_field_path": "activities.0.trainingEffectLabel",
                    "data_type": "string",
                    "unit": "text",
                    "description": "Training effect classification"
                },
                {
                    "metric_name": "swimming_activity_training_load",
                    "api_field_path": "activities.0.activityTrainingLoad",
                    "data_type": "float",
                    "unit": "load",
                    "description": "Training load for the swimming activity"
                }
            ]
        },
        
        # Swimming Lap Metrics (from splits_data)
        {
            "category": "swimming_laps",
            "metrics": [
                {
                    "metric_name": "lap_distance",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.distance",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Distance of individual lap"
                },
                {
                    "metric_name": "lap_duration",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.duration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Duration of individual lap"
                },
                {
                    "metric_name": "lap_moving_duration",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.movingDuration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Moving duration of individual lap"
                },
                {
                    "metric_name": "lap_average_speed",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Average speed of individual lap"
                },
                {
                    "metric_name": "lap_max_speed",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.maxSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Maximum speed of individual lap"
                },
                {
                    "metric_name": "lap_calories",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.calories",
                    "data_type": "float",
                    "unit": "kcal",
                    "description": "Calories burned in individual lap"
                },
                {
                    "metric_name": "lap_average_hr",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageHR",
                    "data_type": "float",
                    "unit": "bpm",
                    "description": "Average heart rate during lap"
                },
                {
                    "metric_name": "lap_max_hr",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.maxHR",
                    "data_type": "float",
                    "unit": "bpm",
                    "description": "Maximum heart rate during lap"
                },
                {
                    "metric_name": "lap_average_swim_cadence",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageSwimCadence",
                    "data_type": "float",
                    "unit": "strokes/min",
                    "description": "Average swimming cadence during lap"
                },
                {
                    "metric_name": "lap_active_lengths",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.numberOfActiveLengths",
                    "data_type": "int",
                    "unit": "lengths",
                    "description": "Number of active lengths in lap"
                },
                {
                    "metric_name": "lap_total_strokes",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.totalNumberOfStrokes",
                    "data_type": "int",
                    "unit": "strokes",
                    "description": "Total strokes in lap"
                },
                {
                    "metric_name": "lap_average_strokes",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageStrokes",
                    "data_type": "float",
                    "unit": "strokes",
                    "description": "Average strokes per length in lap"
                },
                {
                    "metric_name": "lap_average_swolf",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageSWOLF",
                    "data_type": "float",
                    "unit": "swolf",
                    "description": "Average SWOLF score for lap"
                },
                {
                    "metric_name": "lap_average_stroke_distance",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.averageStrokeDistance",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Average stroke distance for lap"
                }
            ]
        },
        
        # Swimming Length Metrics (from splits_data)
        {
            "category": "swimming_lengths",
            "metrics": [
                {
                    "metric_name": "length_distance",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.distance",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Distance of individual length"
                },
                {
                    "metric_name": "length_duration",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.duration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Duration of individual length"
                },
                {
                    "metric_name": "length_average_speed",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.averageSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Average speed of individual length"
                },
                {
                    "metric_name": "length_max_speed",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.maxSpeed",
                    "data_type": "float",
                    "unit": "m/s",
                    "description": "Maximum speed of individual length"
                },
                {
                    "metric_name": "length_average_hr",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.averageHR",
                    "data_type": "float",
                    "unit": "bpm",
                    "description": "Average heart rate during length"
                },
                {
                    "metric_name": "length_max_hr",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.maxHR",
                    "data_type": "float",
                    "unit": "bpm",
                    "description": "Maximum heart rate during length"
                },
                {
                    "metric_name": "length_total_strokes",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.totalNumberOfStrokes",
                    "data_type": "int",
                    "unit": "strokes",
                    "description": "Total strokes in length"
                },
                {
                    "metric_name": "length_average_swolf",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.averageSWOLF",
                    "data_type": "float",
                    "unit": "swolf",
                    "description": "Average SWOLF score for length"
                },
                {
                    "metric_name": "length_swim_stroke",
                    "api_field_path": "activities.0.detailed_data.splits_data.lapDTOs.0.lengthDTOs.0.swimStroke",
                    "data_type": "string",
                    "unit": "stroke_type",
                    "description": "Swimming stroke type for length"
                }
            ]
        },
        
        # Swimming Typed Splits Metrics
        {
            "category": "swimming_typed_splits",
            "metrics": [
                {
                    "metric_name": "typed_split_start_time",
                    "api_field_path": "activities.0.detailed_data.typed_splits.splits.0.startTimeLocal",
                    "data_type": "string",
                    "unit": "datetime",
                    "description": "Start time of typed split"
                },
                {
                    "metric_name": "typed_split_duration",
                    "api_field_path": "activities.0.detailed_data.typed_splits.splits.0.duration",
                    "data_type": "float",
                    "unit": "seconds",
                    "description": "Duration of typed split"
                },
                {
                    "metric_name": "typed_split_distance",
                    "api_field_path": "activities.0.detailed_data.typed_splits.splits.0.distance",
                    "data_type": "float",
                    "unit": "meters",
                    "description": "Distance of typed split"
                },
                {
                    "metric_name": "typed_split_stroke_type",
                    "api_field_path": "activities.0.detailed_data.typed_splits.splits.0.strokeType",
                    "data_type": "string",
                    "unit": "stroke_type",
                    "description": "Stroke type of typed split"
                }
            ]
        }
    ]
    
    # Process each category
    for category in metric_definitions:
        for metric in category["metrics"]:
            # Check if the field exists in the data
            field_path = metric["api_field_path"]
            if _field_exists_in_data(data, field_path):
                metrics.append({
                    "metric_name": metric["metric_name"],
                    "source": "garmin",
                    "api_endpoint": _get_endpoint_from_path(field_path),
                    "api_field_path": field_path,
                    "data_type": metric["data_type"],
                    "unit": metric["unit"],
                    "description": metric["description"]
                })
    
    return metrics


def _field_exists_in_data(data: Dict[str, Any], field_path: str) -> bool:
    """Check if a field path exists in the data."""
    keys = field_path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        else:
            return False
    
    return current is not None


def _get_endpoint_from_path(field_path: str) -> str:
    """Extract the API endpoint from the field path."""
    if field_path.startswith("stats."):
        return "daily_summary"
    elif field_path.startswith("hrv_payload."):
        return "hrv_payload"
    elif field_path.startswith("training_status."):
        return "training_status"
    elif field_path.startswith("activities."):
        return "activities"
    else:
        return "unknown"


async def populate_metrics_config(db_path: str, cache_file_path: str):
    """
    Populate the metrics configuration table with real Garmin API metrics.
    
    Args:
        db_path: Path to the SQLite database
        cache_file_path: Path to the cached Garmin API data
    """
    print("🔧 Setting up database and configuration manager...")
    
    # Initialize database and services
    sqlite_manager = SQLiteManager(db_path)
    sqlite_manager.create_database()
    
    # Create metrics configuration table
    create_metrics_config_table(db_path)
    
    sqlite_client = SQLiteClient(sqlite_manager)
    config_manager = ConfigurationManager(sqlite_client)
    
    print("✅ Database setup complete")
    
    # Analyze cached data to extract metrics
    print(f"\n📊 Analyzing cached data from {cache_file_path}...")
    metrics = analyze_cached_data(cache_file_path)
    print(f"✅ Found {len(metrics)} metrics to add")
    
    # Add metrics to configuration table
    print("\n💾 Adding metrics to configuration table...")
    
    try:
        result = await config_manager.add_metrics(metrics)
        print(f"✅ Successfully added {len(metrics)} metrics to configuration")
        
        # Display summary
        print("\n📋 Metrics Summary:")
        print("=" * 50)
        
        # Group by source
        garmin_metrics = [m for m in metrics if m["source"] == "garmin"]
        print(f"Garmin Metrics: {len(garmin_metrics)}")
        
        # Group by endpoint
        endpoints = {}
        for metric in garmin_metrics:
            endpoint = metric["api_endpoint"]
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(metric["metric_name"])
        
        for endpoint, metric_names in endpoints.items():
            print(f"  {endpoint}: {len(metric_names)} metrics")
            for name in metric_names[:3]:  # Show first 3
                print(f"    - {name}")
            if len(metric_names) > 3:
                print(f"    ... and {len(metric_names) - 3} more")
        
        print("\n🎉 Metrics configuration population completed successfully!")
        
    except Exception as e:
        print(f"❌ Error adding metrics: {e}")
        raise


async def main():
    """Main function to populate metrics configuration."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate metrics configuration table')
    parser.add_argument('--db-path', default='data/health_data.db', 
                       help='Path to SQLite database (default: data/health_data.db)')
    parser.add_argument('--cache-file', default='data/cache/garmin_raw_data_2025-09-12.json',
                       help='Path to cached Garmin API data file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be added without actually adding to database')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made to database")
        metrics = analyze_cached_data(args.cache_file)
        print(f"\n📊 Would add {len(metrics)} metrics:")
        for metric in metrics:
            print(f"  - {metric['metric_name']} ({metric['api_field_path']})")
        return
    
    await populate_metrics_config(args.db_path, args.cache_file)


if __name__ == "__main__":
    asyncio.run(main())
