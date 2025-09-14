"""
Processor for swimming_intervals table.
"""

import logging
from datetime import date
from typing import Dict, Any, List

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import SwimmingInterval

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
        """Transform to SwimmingInterval models."""
        # TODO: Implement transformation logic
        return []
    
    async def load(self, data: List[SwimmingInterval], db_manager: DatabaseManager) -> int:
        """Load SwimmingInterval into database."""
        # TODO: Implement database insertion
        return 0
