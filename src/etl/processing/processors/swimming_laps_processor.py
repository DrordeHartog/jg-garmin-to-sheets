"""
Processor for swimming_laps table.
"""

import logging
from datetime import date
from typing import Dict, Any, List

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import SwimmingLap

logger = logging.getLogger(__name__)


class SwimmingLapsProcessor(BaseTableProcessor):
    """Processor for swimming_laps table."""
    
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Extract swimming laps data from raw API response."""
        laps = []
        
        # Find swimming activities in raw data
        activities = raw_data.get('activities', [])
        swimming_activities = [
            activity for activity in activities
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        logger.info(f"Found {len(swimming_activities)} swimming activities for lap extraction on {target_date}")
        
        for activity in swimming_activities:
            activity_id = activity.get('activityId')
            if not activity_id:
                continue
                
            # Get detailed swimming data
            detailed_data = activity.get('detailed_swimming_data', {})
            splits_data = detailed_data.get('splits_data', {})
            lap_dtos = splits_data.get('lapDTOs', [])
            
            logger.debug(f"Found {len(lap_dtos)} lap DTOs for activity {activity_id}")
            
            for lap_dto in lap_dtos:
                # Extract lap-level data
                lap_data = {
                    'lap_id': f"{activity_id}_{lap_dto.get('lapIndex', 'unknown')}",
                    'session_id': str(activity_id),
                    'lap_index': lap_dto.get('lapIndex'),
                    'wkt_step_index': lap_dto.get('wktStepIndex'),
                    'start_time_gmt': lap_dto.get('startTimeGMT'),
                    'distance': lap_dto.get('distance'),
                    'duration': lap_dto.get('duration'),
                    'moving_duration': lap_dto.get('movingDuration'),
                    'elapsed_duration': lap_dto.get('elapsedDuration'),
                    'average_speed': lap_dto.get('averageSpeed'),
                    'average_moving_speed': lap_dto.get('averageMovingSpeed'),
                    'max_speed': lap_dto.get('maxSpeed'),
                    'calories': lap_dto.get('calories'),
                    'bmr_calories': lap_dto.get('bmrCalories'),
                    'average_hr': lap_dto.get('averageHR'),
                    'max_hr': lap_dto.get('maxHR'),
                    'average_swim_cadence': lap_dto.get('averageSwimCadence'),
                    'number_of_active_lengths': lap_dto.get('numberOfActiveLengths'),
                    'total_strokes': lap_dto.get('totalNumberOfStrokes'),
                    'average_strokes': lap_dto.get('averageStrokes'),
                    'average_swolf': lap_dto.get('averageSWOLF'),
                    'average_stroke_distance': lap_dto.get('averageStrokeDistance'),
                    'swim_drill': lap_dto.get('swimDrill')
                }
                
                laps.append(lap_data)
        
        logger.info(f"Extracted {len(laps)} swimming laps for {target_date}")
        logger.debug(f"Extracted laps data: {laps}")
        return laps
    
    def transform(self, data: List[Dict[str, Any]], target_date: date) -> List[SwimmingLap]:
        """Transform to SwimmingLap models."""
        # TODO: Implement transformation logic
        return []
    
    async def load(self, data: List[SwimmingLap], db_manager: DatabaseManager) -> int:
        """Load SwimmingLap into database."""
        # TODO: Implement database insertion
        return 0
