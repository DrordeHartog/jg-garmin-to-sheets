from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import date
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class GarminAPIRepository:
    def __init__(self, client):
        self.client = client  # garmingo.ingestion.clients.garmin_client.GarminClient
        self._authenticated = False

    async def list_activities(self, day: date) -> List[Dict[str, Any]]:
        """Fetch activities data for a given date."""
        date_iso = day.isoformat()
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_activities_by_date, date_iso, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching activities data for {date_iso}: {str(e)}")
            return None

    async def get_activity_details(self, activity_id: int) -> Dict[str, Any]:
        # TODO: gather splits/typed_splits etc., return dict
        return {}
    
    async def get_recovery_data(self, day: date) -> Dict[str, Any]:
        date_iso = day.isoformat()
        summary, training_status = await asyncio.gather(
            self._fetch_summary_data(date_iso),
            self._fetch_training_status_data(date_iso)
        )
        return {
            'summary': summary,
            'training_status': training_status
        }
    async def get_recovery_metric_details(self, metric_id: str) -> Dict[str, Any]:
        # TODO: gather recovery metric details, return dict
        return {}

    async def _ensure_authenticated(self):
        """Private method - implementation detail."""
        if not self._authenticated:
            # Use environment variables or injected credentials
            email = os.getenv('GARMIN_EMAIL')
            password = os.getenv('GARMIN_PASSWORD')
            await self.client.authenticate(email, password)
            self._authenticated = True
    
    async def _fetch_activities_data(self, date_iso: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch activities data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_activities_by_date, date_iso, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching activities data for {date_iso}: {str(e)}")
            return None

    async def _fetch_summary_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch user summary data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_user_summary, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching summary data for {date_iso}: {str(e)}")
            return None
    
    async def _fetch_training_status_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch training status data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_training_status, date_iso
            )
        except Exception as e:
            logger.error(f"Error fetching training status data for {date_iso}: {str(e)}")
            return None



    async def _fetch_hrv_data(self, target_date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetches HRV data for the given date."""
        try:
            hrv_data = await asyncio.get_event_loop().run_in_executor(
            None, self.client.get_hrv_data, target_date_iso
            )
            logger.debug(f"Raw HRV data for {target_date_iso}: {hrv_data}")
            return hrv_data
        except Exception as e:
            logger.error(f"Error fetching HRV data for {target_date_iso}: {str(e)}")
            return None



