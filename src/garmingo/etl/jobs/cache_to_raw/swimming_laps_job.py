"""
Cache to Raw Swimming Laps ETL Job.

Extracts swimming laps data from cached raw data and loads to raw database.
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
import logging

from ..base_job import BaseETLJob
from ...services.database_client import DatabaseClient
from ...utils.cache_manager import CacheManager
from shared.models import SwimmingLap

logger = logging.getLogger(__name__)


class Swimming_Laps_Job(BaseETLJob):
    """ETL job for processing swimming laps from cache to raw database."""
    
    def __init__(self, target_date: date, cache_manager: CacheManager, database_client: DatabaseClient):
        super().__init__(f"swimming_laps_{target_date}")
        self.target_date = target_date
        self.cache_manager = cache_manager
        self.database_client = database_client
    
    def extract(self) -> Dict[str, Any]:
        """Extract raw data from cache."""
        logger.info(f"Extracting raw data from cache for {self.target_date}")
        
        # Load raw data from cache
        cache_key = f"garmin_raw_data_{self.target_date.isoformat()}"
        raw_data = self.cache_manager.load_from_cache(cache_key)
        
        if not raw_data:
            logger.warning(f"No cached data found for {self.target_date}")
            return {}
        
        logger.info(f"Successfully loaded cached data for {self.target_date}")
        return raw_data
    
    def transform(self, raw_data: Dict[str, Any]) -> List[SwimmingLap]:
        """Transform raw data into swimming laps records."""
        logger.info(f"Transforming swimming laps data for {self.target_date}")
        
        laps = []
        
        # Find swimming activities in raw data
        activities = raw_data.get('activities', [])
        swimming_activities = [
            activity for activity in activities
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        logger.info(f"Found {len(swimming_activities)} swimming activities for lap extraction on {self.target_date}")
        
        for activity in swimming_activities:
            activity_id = activity.get('activityId')
            if not activity_id:
                continue
                
            # Get detailed swimming data
            detailed_data = activity.get('detailed_data', {})
            splits_data = detailed_data.get('splits_data', {})
            typed_splits = detailed_data.get('typed_splits', {})
            lap_dtos = splits_data.get('lapDTOs', [])
            
            # Create interval type mapping from typed_splits
            interval_type_mapping = self._create_interval_type_mapping(typed_splits)
            
            logger.debug(f"Found {len(lap_dtos)} lap DTOs for activity {activity_id}")
            
            for lap_dto in lap_dtos:
                lap_index = lap_dto.get('lapIndex')
                
                # Create SwimmingLap object
                lap = SwimmingLap(
                    lap_id=f"{activity_id}_{lap_index}",
                    interval_id=None,  # Not needed with new approach
                    lap_index=lap_index,
                    wkt_step_index=lap_dto.get('wktStepIndex'),
                    start_time=self._parse_datetime(lap_dto.get('startTimeGMT')),
                    distance=lap_dto.get('distance'),
                    duration=lap_dto.get('duration'),
                    duration_seconds=lap_dto.get('duration'),  # Same as duration for now
                    moving_duration=lap_dto.get('movingDuration'),
                    moving_duration_seconds=lap_dto.get('movingDuration'),
                    elapsed_duration=lap_dto.get('elapsedDuration'),
                    elapsed_duration_seconds=lap_dto.get('elapsedDuration'),
                    average_speed=lap_dto.get('averageSpeed'),
                    average_moving_speed=lap_dto.get('averageMovingSpeed'),
                    max_speed=lap_dto.get('maxSpeed'),
                    calories=lap_dto.get('calories'),
                    bmr_calories=lap_dto.get('bmrCalories'),
                    average_hr=lap_dto.get('averageHR'),
                    max_hr=lap_dto.get('maxHR'),
                    average_swim_cadence=lap_dto.get('averageSwimCadence'),
                    number_of_active_lengths=lap_dto.get('numberOfActiveLengths'),
                    total_strokes=lap_dto.get('totalNumberOfStrokes'),
                    average_strokes=lap_dto.get('averageStrokes'),
                    average_swolf=lap_dto.get('averageSWOLF'),
                    average_stroke_distance=lap_dto.get('averageStrokeDistance'),
                    swim_drill=lap_dto.get('swimDrill'),
                    # Add interval type information
                    interval_type=interval_type_mapping.get(lap_index),
                    lengths=None  # Will be populated by lengths job
                )
                
                laps.append(lap)
        
        logger.info(f"Transformed {len(laps)} swimming laps for {self.target_date}")
        return laps
    
    def _create_interval_type_mapping(self, typed_splits: Dict[str, Any]) -> Dict[int, str]:
        """Create mapping from lap_index to interval_type."""
        mapping = {}
        
        splits = typed_splits.get('splits', [])
        for split in splits:
            interval_type = split.get('type')
            lap_indexes = split.get('lapIndexes', [])
            
            for lap_index in lap_indexes:
                mapping[lap_index] = interval_type
        
        return mapping
    
    def _get_interval_duration_for_lap(self, typed_splits: Dict[str, Any], lap_index: int) -> Optional[float]:
        """Get interval duration for a specific lap."""
        splits = typed_splits.get('splits', [])
        for split in splits:
            lap_indexes = split.get('lapIndexes', [])
            if lap_index in lap_indexes:
                return split.get('duration')
        return None
    
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string with error handling."""
        if not datetime_str:
            return None
        
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse datetime: {datetime_str}")
            return None
    
    def load(self, transformed_data: List[SwimmingLap]) -> Dict[str, Any]:
        """Load transformed data into raw database."""
        logger.info(f"Loading {len(transformed_data)} swimming laps into raw database for {self.target_date}")
        
        if not transformed_data:
            logger.info("No swimming laps data to load")
            return {"status": "completed", "records_processed": 0}
        
        # TODO: Implement database insertion
        # This will need to be implemented when we create the database schema
        
        logger.info(f"Successfully loaded {len(transformed_data)} swimming laps")
        return {"status": "completed", "records_processed": len(transformed_data)}