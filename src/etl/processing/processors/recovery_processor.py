"""
Processor for recovery table.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_processor import BaseTableProcessor, DatabaseManager
from ....shared.models import RecoveryMetrics


class RecoveryProcessor(BaseTableProcessor):
    """Processor for recovery table."""
    
    def extract(self, raw_data: Dict[str, Any], target_date: date) -> Dict[str, Any]:
        """Extract recovery data from raw API response."""
        return {
            'hrv_payload': raw_data.get('hrv_payload'),
            'summary': raw_data.get('summary'),
            'sleep_data': raw_data.get('sleep_data')
        }
    
    def transform(self, data: Dict[str, Any], target_date: date) -> Optional[RecoveryMetrics]:
        """Transform to RecoveryMetrics model."""
        hrv_payload = data.get('hrv_payload')
        summary = data.get('summary')
        sleep_data = data.get('sleep_data')
        
        # Extract HRV data
        hrv_last_night_avg = None
        hrv_status = None
        
        if hrv_payload and hrv_payload.get('hrvSummary'):
            hrv_summary = hrv_payload['hrvSummary']
            hrv_last_night_avg = hrv_summary.get('lastNightAvg')
            hrv_status = hrv_summary.get('status')
        
        # Extract stress and resting HR data
        average_stress = None
        resting_heart_rate = None
        if summary:
            average_stress = summary.get('averageStressLevel')
            resting_heart_rate = summary.get('restingHeartRate')
        
        # Extract key sleep metrics (raw data only)
        sleep_score = None
        sleep_time_seconds = None
        if sleep_data and sleep_data.get('dailySleepDTO'):
            sleep_dto = sleep_data['dailySleepDTO']
            sleep_score = sleep_dto.get('sleepScores', {}).get('overall', {}).get('value')
            sleep_time_seconds = sleep_dto.get('sleepTimeSeconds')
            # Note: We could extract more sleep fields here for a full SleepMetrics object
            # but we're focusing on key recovery-relevant sleep metrics
        
        # Create RecoveryMetrics (missing fields will be None)
        return RecoveryMetrics(
            date=target_date,
            hrv_last_night_avg=hrv_last_night_avg,
            hrv_weekly_avg=None,  # Not available in current API
            hrv_last_night_5min_high=None,  # Not available in current API
            hrv_status=hrv_status,
            hrv_feedback_phrase=None,  # Not available in current API
            average_stress=average_stress,
            resting_heart_rate=resting_heart_rate,
            sleep_score=sleep_score,
            sleep_time_seconds=sleep_time_seconds
        )
    
    async def load(self, data: Optional[RecoveryMetrics], db_manager: DatabaseManager) -> int:
        """Load RecoveryMetrics into database."""
        if not data:
            return 0
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO recovery (
                    date, hrv_last_night_avg, hrv_weekly_avg, hrv_last_night_5min_high,
                    hrv_status, hrv_feedback_phrase, average_stress, resting_heart_rate,
                    sleep_score, sleep_time_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.date.isoformat(),
                data.hrv_last_night_avg,
                data.hrv_weekly_avg,
                data.hrv_last_night_5min_high,
                data.hrv_status,
                data.hrv_feedback_phrase,
                data.average_stress,
                data.resting_heart_rate,
                data.sleep_score,
                data.sleep_time_seconds
            ))
            conn.commit()  # Commit the transaction
            return 1