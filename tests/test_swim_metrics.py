import asyncio
from datetime import date
from src.garmin_client import GarminClient


def test_swim_metrics_aggregated(monkeypatch):
    gc = GarminClient("email", "password")
    gc._authenticated = True

    activity = {
        'activityType': {'typeKey': 'pool_swim', 'parentTypeId': 17},
        'distance': 500,  # meters
        'duration': 900,  # seconds
        'lapCount': 20,
        'activityId': 123,
    }

    monkeypatch.setattr(gc.client, 'get_stats_and_body', lambda d: {})
    monkeypatch.setattr(gc.client, 'get_sleep_data', lambda d: {})
    monkeypatch.setattr(gc.client, 'get_activities_by_date', lambda s, e: [activity])
    monkeypatch.setattr(gc.client, 'get_user_summary', lambda d: {})
    monkeypatch.setattr(gc.client, 'get_training_status', lambda d: {})

    async def fake_hrv(self, iso):
        return None

    monkeypatch.setattr(GarminClient, '_fetch_hrv_data', fake_hrv, raising=False)

    monkeypatch.setattr(
        gc.client,
        'get_activity',
        lambda aid: {
            'summaryDTO': {
                'avgSwolf': 40,
                'totalNumberOfStrokes': 300,
                'numberOfLaps': 20,
            }
        },
    )

    metrics = asyncio.run(gc.get_metrics(date(2023, 1, 1)))

    assert metrics.swim_activity_count == 1
    assert metrics.swim_distance_km == 0.5
    assert metrics.swim_duration_min == 15
    assert metrics.swim_laps == 20
    assert metrics.pool_swim_count == 1
    assert metrics.open_water_swim_count == 0
    assert metrics.avg_swolf == 40
    assert metrics.total_strokes == 300
