"""
Garmin API to Cache ETL Job.

Extracts data from Garmin Connect API and loads to cache.
"""

from datetime import date
from typing import Dict, Any, Optional
import asyncio
import logging

from ..base_job import BaseETLJob
from ...services.garmin_client import GarminClient
from ...utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class Garmin_API_Data_Job(BaseETLJob):
    """ETL job for fetching Garmin data from API and caching it."""
    
    def __init__(self, target_date: date, garmin_client: GarminClient, cache_manager: CacheManager):
        super().__init__(f"garmin_api_to_cache_{target_date}")
        self.target_date = target_date
        self.garmin_client = garmin_client
        self.cache_manager = cache_manager
    
    def extract(self) -> Dict[str, Any]:
        """Extract raw data from Garmin API."""
        logger.info(f"Fetching raw data from Garmin API for {self.target_date}")
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, need to use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._run_async_fetch)
                raw_data = future.result()
        except RuntimeError:
            # No event loop running, we can create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                raw_data = loop.run_until_complete(
                    self.garmin_client.fetch_raw_data_for_date(self.target_date)
                )
            finally:
                loop.close()
        
        logger.info(f"Successfully fetched raw data for {self.target_date}")
        return raw_data
    
    def _run_async_fetch(self) -> Dict[str, Any]:
        """Helper method to run async fetch in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Get basic raw data first
            raw_data = loop.run_until_complete(
                self.garmin_client.fetch_raw_data_for_date(self.target_date)
            )
            
            # Add detailed swimming data if there are swimming activities
            raw_data = loop.run_until_complete(
                self._add_detailed_swimming_data(raw_data)
            )
            
            return raw_data
        finally:
            loop.close()
    
    async def _add_detailed_swimming_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add detailed swimming data to the raw data."""
        activities = raw_data.get('activities', [])
        if not activities:
            return raw_data
        
        # Find swimming activities
        swimming_activities = []
        for activity in activities:
            activity_type = activity.get('activityType', {})
            type_key = activity_type.get('typeKey', '').lower()
            parent_type_id = activity_type.get('parentTypeId')
            
            if 'swim' in type_key or (parent_type_id == 26 and type_key == 'lap_swimming'):
                swimming_activities.append(activity)
        
        if not swimming_activities:
            return raw_data
        
        # Fetch detailed data for each swimming activity
        detailed_activities = []
        for activity in swimming_activities:
            activity_id = activity.get('activityId')
            if activity_id:
                try:
                    # Fetch detailed splits data
                    splits_data = await asyncio.get_event_loop().run_in_executor(
                        None, self.garmin_client.client.get_activity_splits, activity_id
                    )
                    split_summaries = await asyncio.get_event_loop().run_in_executor(
                        None, self.garmin_client.client.get_activity_split_summaries, activity_id
                    )
                    typed_splits = await asyncio.get_event_loop().run_in_executor(
                        None, self.garmin_client.client.get_activity_typed_splits, activity_id
                    )
                    
                    # Add detailed data to activity
                    activity_with_details = activity.copy()
                    activity_with_details['detailed_data'] = {
                        'splits_data': splits_data,
                        'split_summaries': split_summaries,
                        'typed_splits': typed_splits
                    }
                    detailed_activities.append(activity_with_details)
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch detailed data for activity {activity_id}: {e}")
                    detailed_activities.append(activity)
            else:
                detailed_activities.append(activity)
        
        # Update the raw data with detailed activities
        raw_data['activities'] = detailed_activities
        return raw_data
    
    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """No transformation - keep raw JSON data."""
        logger.debug(f"No transformation needed for {self.target_date} - keeping raw data")
        return raw_data
    
    def load(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load raw data to cache."""
        logger.info(f"Saving raw data to cache for {self.target_date}")
        
        # Save raw data to cache
        cache_key = f"garmin_raw_data_{self.target_date.isoformat()}"
        self.cache_manager.save_to_cache(cache_key, transformed_data)
        
        logger.info(f"Successfully cached raw data for {self.target_date}")
        return {"status": "cached", "cache_key": cache_key}
