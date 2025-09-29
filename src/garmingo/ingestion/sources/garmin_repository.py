from __future__ import annotations
from typing import List, Dict, Any
from datetime import date

class GarminAPIRepository:
    def __init__(self, client):
        self.client = client  # garmingo.ingestion.clients.garmin_client.GarminClient

    def list_sessions(self, day: date) -> List[Dict[str, Any]]:
        # TODO: call client endpoints, handle pagination, return list of dicts
        return []

    def get_session_details(self, activity_id: int) -> Dict[str, Any]:
        # TODO: gather splits/typed_splits etc., return dict
        return {}
