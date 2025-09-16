"""
Processor for swimming_lengths table.
"""

import logging
from datetime import date
from typing import Dict, Any, List

from .base_processor import BaseTableProcessor, DatabaseManager
from shared.models import SwimmingLength

logger = logging.getLogger(__name__)


class SwimmingLengthsProcessor(BaseTableProcessor):
    """Processor for swimming_lengths table."""
    
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Extract swimming lengths data from raw API response."""
        lengths = []
        
        # Find swimming activities in raw data
        activities = raw_data.get('activities', [])
        swimming_activities = [
            activity for activity in activities
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        logger.info(f"Found {len(swimming_activities)} swimming activities for length extraction on {target_date}")
        
        for activity in swimming_activities:
            activity_id = activity.get('activityId')
            if not activity_id:
                continue
                
            # Get detailed swimming data
            detailed_data = activity.get('detailed_swimming_data', {})
            splits_data = detailed_data.get('splits_data', {})
            lap_dtos = splits_data.get('lapDTOs', [])
            
            logger.debug(f"Found {len(lap_dtos)} lap DTOs for length extraction from activity {activity_id}")
            
            for lap_dto in lap_dtos:
                lap_index = lap_dto.get('lapIndex')
                length_dtos = lap_dto.get('lengthDTOs', [])
                
                logger.debug(f"Found {len(length_dtos)} length DTOs in lap {lap_index}")
                
                for length_dto in length_dtos:
                    # Extract length-level data
                    length_data = {
                        'length_id': f"{activity_id}_{lap_index}_{length_dto.get('lengthIndex', 'unknown')}",
                        'lap_id': f"{activity_id}_{lap_index}",
                        'session_id': str(activity_id),
                        'lap_index': lap_index,
                        'length_index': length_dto.get('lengthIndex'),
                        'start_time_gmt': length_dto.get('startTimeGMT'),
                        'distance': length_dto.get('distance'),
                        'duration': length_dto.get('duration'),
                        'average_speed': length_dto.get('averageSpeed'),
                        'max_speed': length_dto.get('maxSpeed'),
                        'average_hr': length_dto.get('averageHR'),
                        'max_hr': length_dto.get('maxHR'),
                        'total_strokes': length_dto.get('totalNumberOfStrokes'),
                        'swim_stroke': length_dto.get('swimStroke'),
                        'average_swolf': length_dto.get('averageSWOLF')
                    }
                    
                    lengths.append(length_data)
        
        logger.info(f"Extracted {len(lengths)} swimming lengths for {target_date}")
        logger.debug(f"Extracted lengths data: {lengths}")
        return lengths
    
    def transform(self, data: List[Dict[str, Any]], target_date: date) -> List[SwimmingLength]:
        """Transform to SwimmingLength models."""
        # TODO: Implement transformation logic
        return []
    
    async def load(self, data: List[SwimmingLength], db_manager: DatabaseManager) -> int:
        """Load SwimmingLength into database."""
        # TODO: Implement database insertion
        return 0
