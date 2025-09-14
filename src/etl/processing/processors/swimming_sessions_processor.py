"""
Processor for swimming_sessions table.
"""

import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import SwimmingSession
from ..utils.swimming_utils import (
    convert_duration_to_seconds_and_hms,
    calculate_pace_per_100m_hms,
    calculate_strokes_per_length,
    calculate_strokes_per_minute,
    determine_swim_type_counts
)

logger = logging.getLogger(__name__)


class SwimmingSessionsProcessor(BaseTableProcessor):
    """Processor for swimming_sessions table."""
    
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Extract swimming sessions data from raw API response."""
        sessions = []
        
        # Find swimming activities in raw data
        activities = raw_data.get('activities', [])
        swimming_activities = [
            activity for activity in activities 
            if activity.get('activityType', {}).get('typeKey') == 'lap_swimming'
        ]
        
        for activity in swimming_activities:
            # Extract session-level summary data only
            session_data = {
                'session_id': str(activity.get('activityId', '')),
                'activity_id': activity.get('activityId'),
                'activity_name': activity.get('activityName', ''),
                'start_time_local': activity.get('startTimeLocal'),
                'start_time_gmt': activity.get('startTimeGMT'),
                'end_time_local': activity.get('endTimeLocal'),
                'end_time_gmt': activity.get('endTimeGMT'),
                'total_distance': activity.get('distance'),
                'total_duration': activity.get('duration'),
                'elapsed_duration': activity.get('elapsedDuration'),
                'moving_duration': activity.get('movingDuration'),
                'average_speed': activity.get('averageSpeed'),
                'max_speed': activity.get('maxSpeed'),
                'average_hr': activity.get('averageHR'),
                'max_hr': activity.get('maxHR'),
                'min_hr': activity.get('minHR'),
                'calories': activity.get('calories'),
                'pool_length': activity.get('poolLength'),
                'lap_count': activity.get('lapCount'),
                'active_lengths': activity.get('activeLengths'),
                'device_id': activity.get('deviceId'),
                'event_type': activity.get('eventType', {}).get('typeKey'),
                'activity_type': activity.get('activityType', {}).get('typeKey')
            }
            
            # Only include sessions with valid session_id
            if session_data['session_id']:
                sessions.append(session_data)
        
        logger.info(f"Extracted {len(sessions)} swimming sessions for {target_date}")
        logger.debug(f"Extracted sessions data: {sessions}")
        return sessions
    
    def transform(self, data: List[Dict[str, Any]], target_date: date) -> List[SwimmingSession]:
        """Transform extracted data to SwimmingSessionRecord models."""
        transformed_sessions = []
        
        for session_data in data:
            try:
                transformed_session = self._transform_single_session(session_data, target_date)
                transformed_sessions.append(transformed_session)
                logger.debug(f"Transformed session {session_data['session_id']}")
                
            except Exception as e:
                logger.error(f"Failed to transform session {session_data.get('session_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Transformed {len(transformed_sessions)} swimming sessions for {target_date}")
        return transformed_sessions
    
    def _transform_single_session(self, session_data: Dict[str, Any], target_date: date) -> SwimmingSession:
        """Transform a single session data dictionary to SwimmingSessionRecord."""
        # Parse datetime fields
        start_time = self._parse_datetime(session_data.get('start_time_gmt'), 'start_time_gmt')
        end_time = self._parse_datetime(session_data.get('end_time_gmt'), 'end_time_gmt')
        
        # Convert duration to both seconds and HH:MM:SS format
        total_duration_seconds, total_duration_hms = convert_duration_to_seconds_and_hms(
            session_data.get('total_duration')
        )
        
        # Calculate derived metrics using shared utilities
        pace_per_100m_seconds, pace_per_100m_hms = calculate_pace_per_100m_hms(session_data)
        strokes_per_length = calculate_strokes_per_length(session_data)
        strokes_per_minute = calculate_strokes_per_minute(session_data)
        
        # Determine swim type counts
        pool_swim_count, open_water_swim_count = determine_swim_type_counts(session_data)
        
        return SwimmingSession(
            session_id=session_data['session_id'],
            activity_id=session_data.get('activity_id'),
            date=target_date,
            start_time=start_time,
            end_time=end_time,
            total_distance_meters=session_data.get('total_distance'),
            total_duration_seconds=total_duration_seconds,
            pool_length_meters=session_data.get('pool_length'),
            swim_activity_count=1,  # This is one swimming activity
            pool_swim_count=pool_swim_count,
            open_water_swim_count=open_water_swim_count,
            swim_laps=session_data.get('lap_count'),
            active_lengths=session_data.get('active_lengths'),
            swim_average_pace_per_100m=pace_per_100m_seconds,
            swim_average_speed=session_data.get('average_speed'),
            swim_max_speed=session_data.get('max_speed'),
            swim_average_hr=session_data.get('average_hr'),
            swim_max_hr=session_data.get('max_hr'),
            total_strokes=session_data.get('total_strokes'),
            swim_average_strokes_per_length=strokes_per_length,
            swim_average_strokes_per_minute=strokes_per_minute,
            swim_calories=session_data.get('calories')
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
    
    
    async def load(self, data: List[SwimmingSession], db_manager: DatabaseManager) -> int:
        """Load SwimmingSession into database."""
        # TODO: Implement database insertion
        return 0
