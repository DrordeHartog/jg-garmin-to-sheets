"""
Processor for swimming_laps table.
"""

import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from .base_processor import BaseTableProcessor, DatabaseManager
from shared.models import SwimmingLap
from ..utils.swimming_utils import convert_duration_to_seconds_and_hms

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
        """Transform extracted data to SwimmingLapRecord models."""
        transformed_laps = []
        
        for lap_data in data:
            try:
                transformed_lap = self._transform_single_lap(lap_data, target_date)
                transformed_laps.append(transformed_lap)
                logger.debug(f"Transformed lap {lap_data['lap_id']}")
                
            except Exception as e:
                logger.error(f"Failed to transform lap {lap_data.get('lap_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Transformed {len(transformed_laps)} swimming laps for {target_date}")
        logger.info(f"Transformed laps data: {transformed_laps}")
        return transformed_laps
    
    def _transform_single_lap(self, lap_data: Dict[str, Any], target_date: date) -> SwimmingLap:
        """Transform a single lap data dictionary to SwimmingLapRecord."""
        # Parse datetime fields
        start_time = self._parse_datetime(lap_data.get('start_time_gmt'), 'start_time_gmt')
        
        # Convert durations using shared utility
        duration_seconds, duration_hms = convert_duration_to_seconds_and_hms(lap_data.get('duration'))
        moving_duration_seconds, moving_duration_hms = convert_duration_to_seconds_and_hms(lap_data.get('moving_duration'))
        elapsed_duration_seconds, elapsed_duration_hms = convert_duration_to_seconds_and_hms(lap_data.get('elapsed_duration'))
        
        return SwimmingLap(
            lap_id=lap_data['lap_id'],
            interval_id=None,  # Will be set during load phase when we have interval mapping
            lap_index=lap_data.get('lap_index'),
            wkt_step_index=lap_data.get('wkt_step_index'),
            start_time=start_time,
            distance=lap_data.get('distance'),
            duration=lap_data.get('duration'),  # Raw duration from API
            duration_seconds=duration_seconds,  # Converted duration in seconds
            moving_duration=lap_data.get('moving_duration'),  # Raw moving duration
            moving_duration_seconds=moving_duration_seconds,  # Converted moving duration
            elapsed_duration=lap_data.get('elapsed_duration'),  # Raw elapsed duration
            elapsed_duration_seconds=elapsed_duration_seconds,  # Converted elapsed duration
            average_speed=lap_data.get('average_speed'),
            average_moving_speed=lap_data.get('average_moving_speed'),
            max_speed=lap_data.get('max_speed'),
            calories=lap_data.get('calories'),
            bmr_calories=lap_data.get('bmr_calories'),
            average_hr=lap_data.get('average_hr'),
            max_hr=lap_data.get('max_hr'),
            average_swim_cadence=lap_data.get('average_swim_cadence'),
            number_of_active_lengths=lap_data.get('number_of_active_lengths'),
            total_strokes=lap_data.get('total_strokes'),
            average_strokes=lap_data.get('average_strokes'),
            average_swolf=lap_data.get('average_swolf'),
            average_stroke_distance=lap_data.get('average_stroke_distance'),
            swim_drill=lap_data.get('swim_drill')
        )
    
    def _parse_datetime(self, datetime_str: Optional[str], field_name: str) -> Optional[datetime]:
        """Parse datetime string with error handling."""
        if not datetime_str:
            return None
        
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse {field_name}: {datetime_str}")
            return None
    
    async def load(self, data: List[SwimmingLap], db_manager: DatabaseManager) -> int:
        """Load SwimmingLap data into database using batch insertion."""
        if not data:
            return 0
        
        # Prepare batch data for insertion
        batch_data = []
        for lap in data:
            # Split lap_id to get session_id and lap_index
            session_id, lap_index = lap.lap_id.split('_', 1)
            
            batch_data.append((
                lap.lap_id,  # lap_id as primary key
                session_id,  # session_id as foreign key
                int(lap_index),  # Convert lap_index to int
                lap.start_time.isoformat() if lap.start_time else None,
                lap.distance,
                lap.duration_seconds,
                lap.moving_duration_seconds,
                lap.elapsed_duration_seconds,
                lap.average_speed,
                lap.average_moving_speed,
                lap.max_speed,
                lap.calories,
                lap.bmr_calories,
                lap.average_hr,
                lap.max_hr,
                lap.average_swim_cadence,
                lap.number_of_active_lengths,
                lap.total_strokes,
                lap.average_strokes,
                lap.average_swolf,
                lap.average_stroke_distance,
                lap.swim_drill
            ))

        # Batch insert all laps
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO swimming_laps (
                    lap_id, session_id, lap_index, start_time, distance_meters,
                    duration_seconds, moving_duration_seconds, elapsed_duration_seconds,
                    average_speed, average_moving_speed, max_speed, calories, bmr_calories,
                    average_hr, max_hr, average_swim_cadence, number_of_active_lengths,
                    total_strokes, average_strokes, average_swolf, average_stroke_distance, swim_drill
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            conn.commit()

        logger.info(f"Batch loaded {len(batch_data)} swimming laps to database")
        return len(batch_data)
    
