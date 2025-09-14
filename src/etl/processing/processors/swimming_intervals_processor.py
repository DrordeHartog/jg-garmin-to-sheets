"""
Processor for swimming_intervals table.
"""

import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import SwimmingInterval
from ..utils.swimming_utils import convert_duration_to_seconds_and_hms

logger = logging.getLogger(__name__)


class SwimmingIntervalsProcessor(BaseTableProcessor):
    """Processor for swimming_intervals table."""
    
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Extract swimming intervals data from raw API response."""
        intervals = []
        
        # Find swimming activities in raw data
        activities = raw_data.get('activities', [])
        swimming_activities = [
            activity for activity in activities
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        logger.info(f"Found {len(swimming_activities)} swimming activities for interval extraction on {target_date}")
        
        for activity in swimming_activities:
            activity_id = activity.get('activityId')
            if not activity_id:
                continue
                
            # Get detailed split summaries from detailed_swimming_data
            detailed_data = activity.get('detailed_swimming_data', {})
            split_summaries_data = detailed_data.get('split_summaries', {})
            split_summaries = split_summaries_data.get('splitSummaries', [])
            
            logger.debug(f"Found {len(split_summaries)} split summaries for activity {activity_id}")
            
            for interval_idx, split_summary in enumerate(split_summaries):
                # Extract interval-level data
                interval_data = {
                    'interval_id': f"{activity_id}_{interval_idx}",
                    'session_id': str(activity_id),
                    'interval_index': interval_idx,
                    'split_type': split_summary.get('splitType'),
                    'no_of_splits': split_summary.get('noOfSplits'),
                    'duration': split_summary.get('duration'),
                    'distance': split_summary.get('distance'),
                    'moving_duration': split_summary.get('movingDuration'),
                    'average_speed': split_summary.get('averageSpeed'),
                    'calories': split_summary.get('calories'),
                    'bmr_calories': split_summary.get('bmrCalories'),
                    'average_hr': split_summary.get('averageHR'),
                    'max_hr': split_summary.get('maxHR'),
                    'total_exercise_reps': split_summary.get('totalExerciseReps'),
                    'max_distance': split_summary.get('maxDistance'),
                    'max_distance_with_precision': split_summary.get('maxDistanceWithPrecision')
                }
                
                intervals.append(interval_data)
        
        logger.info(f"Extracted {len(intervals)} swimming intervals for {target_date}")
        logger.debug(f"Extracted intervals data: {intervals}")
        return intervals
    
    def transform(self, data: List[Dict[str, Any]], target_date: date) -> List[SwimmingInterval]:
        """Transform extracted data to SwimmingInterval models."""
        transformed_intervals = []
        
        for interval_data in data:
            try:
                transformed_interval = self._transform_single_interval(interval_data, target_date)
                transformed_intervals.append(transformed_interval)
                logger.debug(f"Transformed interval {interval_data['interval_id']}")
                
            except Exception as e:
                logger.error(f"Failed to transform interval {interval_data.get('interval_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Transformed {len(transformed_intervals)} swimming intervals for {target_date}")
        logger.info(f"Transformed intervals data: {transformed_intervals}")
        return transformed_intervals
    
    def _transform_single_interval(self, interval_data: Dict[str, Any], target_date: date) -> SwimmingInterval:
        """Transform a single interval data dictionary to SwimmingIntervalRecord."""
        # Parse datetime fields (intervals typically don't have start/end times in split summaries)
        start_time = None  # Split summaries don't contain start/end times
        end_time = None
        
        # Convert durations using shared utility
        duration_seconds, duration_hms = convert_duration_to_seconds_and_hms(interval_data.get('duration'))
        moving_duration_seconds, moving_duration_hms = convert_duration_to_seconds_and_hms(interval_data.get('moving_duration'))
        
        return SwimmingInterval(
            interval_id=interval_data['interval_id'],
            session_id=interval_data['session_id'],
            interval_type=interval_data.get('split_type'),
            start_time=start_time,
            end_time=end_time,
            distance=interval_data.get('distance'),
            duration=interval_data.get('duration'),  # Raw duration from API
            duration_seconds=duration_seconds,  # Converted duration in seconds
            moving_duration=interval_data.get('moving_duration'),  # Raw moving duration
            moving_duration_seconds=moving_duration_seconds,  # Converted moving duration
            elapsed_duration=None,  # Not available in split summaries
            elapsed_duration_seconds=None,  # Not available in split summaries
            average_speed=interval_data.get('average_speed'),
            calories=interval_data.get('calories'),
            bmr_calories=interval_data.get('bmr_calories'),
            average_hr=interval_data.get('average_hr'),
            max_hr=interval_data.get('max_hr'),
            total_exercise_reps=interval_data.get('total_exercise_reps'),
            message_index=None  # Not available in split summaries
        )
    
    async def load(self, data: List[SwimmingInterval], db_manager: DatabaseManager) -> int:
        """Load SwimmingInterval data into database using batch insertion."""
        if not data:
            return 0
        
        # Prepare batch data for insertion
        batch_data = []
        for interval in data:
            batch_data.append((
                interval.session_id,
                interval.interval_type,
                interval.start_time.isoformat() if interval.start_time else None,
                interval.end_time.isoformat() if interval.end_time else None,
                interval.duration_seconds,
                interval.moving_duration_seconds,
                interval.elapsed_duration_seconds,
                interval.distance,
                interval.average_speed,
                interval.calories,
                interval.bmr_calories,
                interval.average_hr,
                interval.max_hr,
                interval.total_exercise_reps,
                interval.message_index
            ))
        
        # Batch insert all intervals
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO swimming_intervals (
                    session_id, interval_type, start_time, end_time,
                    duration_seconds, moving_duration_seconds, elapsed_duration_seconds,
                    distance_meters, average_speed, calories, bmr_calories,
                    average_hr, max_hr, total_exercise_reps, message_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()
        
        logger.info(f"Batch loaded {len(batch_data)} swimming intervals to database")
        return len(batch_data)
