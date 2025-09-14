"""
Processor for swimming_sessions table.
"""

import logging
from datetime import date
from typing import Dict, Any, List

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import SwimmingSession

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
        """Transform to SwimmingSession models."""
        # TODO: Implement transformation logic
        return []
    
    async def load(self, data: List[SwimmingSession], db_manager: DatabaseManager) -> int:
        """Load SwimmingSession into database."""
        # TODO: Implement database insertion
        return 0
