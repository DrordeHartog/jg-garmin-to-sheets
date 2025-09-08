"""
Tests for data fetching logic in GarminClient.
"""
import pytest
import asyncio
from datetime import date
from unittest.mock import patch, AsyncMock
from src.core.garmin_client import GarminClient
from src.core.models import DailyMetrics, SleepMetrics, HealthMetrics, RecoveryMetrics, SwimmingMetrics


class TestGarminClientDataFetching:
    """Test the data fetching methods."""
    
    @pytest.mark.asyncio
    async def test_fetch_stats_data_success(self):
        """Test successful stats data fetching."""
        client = GarminClient()
        
        # Mock the client and executor
        with patch.object(client, 'client') as mock_client:
            mock_client.get_stats_and_body.return_value = {'weight': 70000, 'bodyFat': 15.5}
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(return_value={'weight': 70000, 'bodyFat': 15.5})
                
                result = await client._fetch_stats_data('2024-01-15')
                
                assert result == {'weight': 70000, 'bodyFat': 15.5}
                # The method is called through run_in_executor, so we check the executor call
                mock_loop.return_value.run_in_executor.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_stats_data_error(self):
        """Test stats data fetching with error."""
        client = GarminClient()
        
        # Mock the client to raise an exception
        with patch.object(client, 'client') as mock_client:
            mock_client.get_stats_and_body.side_effect = Exception("API Error")
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(side_effect=Exception("API Error"))
                
                result = await client._fetch_stats_data('2024-01-15')
                
                assert result is None

    @pytest.mark.asyncio
    async def test_fetch_sleep_data_success(self):
        """Test successful sleep data fetching."""
        client = GarminClient()
        
        # Mock the client and executor
        with patch.object(client, 'client') as mock_client:
            mock_client.get_sleep_data.return_value = {'dailySleepDTO': {'sleepTimeSeconds': 28800}}
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(return_value={'dailySleepDTO': {'sleepTimeSeconds': 28800}})
                
                result = await client._fetch_sleep_data('2024-01-15')
                
                assert result == {'dailySleepDTO': {'sleepTimeSeconds': 28800}}
                # The method is called through run_in_executor, so we check the executor call
                mock_loop.return_value.run_in_executor.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_activities_data_success(self):
        """Test successful activities data fetching."""
        client = GarminClient()
        
        # Mock the client and executor
        with patch.object(client, 'client') as mock_client:
            mock_client.get_activities_by_date.return_value = [{'activityType': {'typeKey': 'running'}}]
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(return_value=[{'activityType': {'typeKey': 'running'}}])
                
                result = await client._fetch_activities_data('2024-01-15')
                
                assert result == [{'activityType': {'typeKey': 'running'}}]
                # The method is called through run_in_executor, so we check the executor call
                mock_loop.return_value.run_in_executor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_raw_data_with_real_credentials(self):
        """Test data fetching with real Garmin credentials - INTEGRATION TEST."""
        from dotenv import load_dotenv
        import os
        from src.utils import setup_custom_logging, get_logger, log_swimming_data
        
        # Setup logging to file for this test
        setup_custom_logging(level="DEBUG", output="file", log_file="logs/test_data_fetching.log")
        logger = get_logger(__name__)
        
        load_dotenv()

        client = GarminClient()
        
        # Use real credentials from environment
        email = os.getenv("USER1_GARMIN_EMAIL")
        password = os.getenv("USER1_GARMIN_PASSWORD")
        
        if not email or not password:
            pytest.skip("Real Garmin credentials not available in environment")
        
        try:
            logger.info(f"Starting real data fetch test for {email}")
            
            # Authenticate first
            await client.authenticate(email, password)
            logger.info("Authentication successful")
            
            # Test fetching raw data for a recent date
            from datetime import date, timedelta
            test_date = date.today() - timedelta(days=1)  # Yesterday
            logger.info(f"Fetching data for date: {test_date}")
            
            result = await client._fetch_raw_data(test_date)
            
            # Verify we got a dictionary with all expected keys
            assert isinstance(result, dict)
            assert 'stats' in result
            assert 'sleep_data' in result
            assert 'activities' in result
            assert 'summary' in result
            assert 'training_status' in result
            assert 'hrv_payload' in result
            
            # Verify at least some data is present (not all None)
            data_present = any(result[key] is not None for key in result.keys())
            assert data_present, "At least some data should be present"
            
            # Log detailed data information
            logger.info(f"✅ Successfully fetched raw data for {test_date}")
            logger.info(f"   Stats: {'Present' if result['stats'] else 'None'}")
            logger.info(f"   Sleep: {'Present' if result['sleep_data'] else 'None'}")
            logger.info(f"   Activities: {'Present' if result['activities'] else 'None'}")
            logger.info(f"   Summary: {'Present' if result['summary'] else 'None'}")
            logger.info(f"   Training Status: {'Present' if result['training_status'] else 'None'}")
            logger.info(f"   HRV: {'Present' if result['hrv_payload'] else 'None'}")
            
            # Use enhanced swimming data logging
            logger.info("=== COMPREHENSIVE SWIMMING DATA ANALYSIS ===")
            
            # Analyze each data type for swimming content
            log_swimming_data(logger, result['stats'], "stats")
            log_swimming_data(logger, result['sleep_data'], "sleep_data")
            log_swimming_data(logger, result['activities'], "activities")
            log_swimming_data(logger, result['summary'], "summary")
            log_swimming_data(logger, result['training_status'], "training_status")
            log_swimming_data(logger, result['hrv_payload'], "hrv_payload")
            
            logger.info("=== END COMPREHENSIVE SWIMMING DATA ANALYSIS ===")
            
            print(f"✅ Successfully fetched raw data for {test_date}")
            print(f"   Check logs/test_data_fetching.log for detailed data")
            
        except Exception as e:
            logger.error(f"Real data fetching failed: {e}")
            pytest.fail(f"Real data fetching failed: {e}")

    @pytest.mark.asyncio
    async def test_fetch_raw_data_success(self):
        """Test successful concurrent data fetching."""
        from datetime import date
        
        client = GarminClient()
        
        # Mock all the individual fetch methods
        with patch.object(client, '_fetch_stats_data', new_callable=AsyncMock) as mock_stats, \
             patch.object(client, '_fetch_sleep_data', new_callable=AsyncMock) as mock_sleep, \
             patch.object(client, '_fetch_activities_data', new_callable=AsyncMock) as mock_activities, \
             patch.object(client, '_fetch_summary_data', new_callable=AsyncMock) as mock_summary, \
             patch.object(client, '_fetch_training_status_data', new_callable=AsyncMock) as mock_training, \
             patch.object(client, '_fetch_hrv_data', new_callable=AsyncMock) as mock_hrv:
            
            # Set up mock return values
            mock_stats.return_value = {'weight': 70000, 'bodyFat': 15.5}
            mock_sleep.return_value = {'dailySleepDTO': {'sleepTimeSeconds': 28800}}
            mock_activities.return_value = [{'activityType': {'typeKey': 'running'}}]
            mock_summary.return_value = {'activeKilocalories': 500}
            mock_training.return_value = {'mostRecentVO2Max': {'generic': {'vo2MaxValue': 45.0}}}
            mock_hrv.return_value = {'hrvSummary': {'lastNightAvg': 45, 'status': 'BALANCED'}}
            
            # Test the method
            target_date = date(2024, 1, 15)
            result = await client._fetch_raw_data(target_date)
            
            # Verify the result structure
            assert isinstance(result, dict)
            assert 'stats' in result
            assert 'sleep_data' in result
            assert 'activities' in result
            assert 'summary' in result
            assert 'training_status' in result
            assert 'hrv_payload' in result
            
            # Verify the data
            assert result['stats']['weight'] == 70000
            assert result['sleep_data']['dailySleepDTO']['sleepTimeSeconds'] == 28800
            assert len(result['activities']) == 1
            assert result['summary']['activeKilocalories'] == 500
            assert result['training_status']['mostRecentVO2Max']['generic']['vo2MaxValue'] == 45.0
            assert result['hrv_payload']['hrvSummary']['lastNightAvg'] == 45
            
            # Verify all methods were called with correct date
            mock_stats.assert_called_once_with('2024-01-15')
            mock_sleep.assert_called_once_with('2024-01-15')
            mock_activities.assert_called_once_with('2024-01-15')
            mock_summary.assert_called_once_with('2024-01-15')
            mock_training.assert_called_once_with('2024-01-15')
            mock_hrv.assert_called_once_with('2024-01-15')

    @pytest.mark.asyncio
    async def test_fetch_raw_data_with_none_values(self):
        """Test data fetching when some APIs return None."""
        from datetime import date
        
        client = GarminClient()
        
        # Mock the client methods to return None for some data
        with patch.object(client, 'client') as mock_client:
            # Mock the executor to return None for some calls
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(side_effect=[
                    None,  # stats - no data
                    {'dailySleepDTO': {'sleepTimeSeconds': 28800}},  # sleep - has data
                    None,  # activities - no data
                    {'activeKilocalories': 500},  # summary - has data
                    None  # training_status - no data
                ])
                
                # Mock _fetch_hrv_data to return None
                with patch.object(client, '_fetch_hrv_data', new_callable=AsyncMock) as mock_hrv:
                    mock_hrv.return_value = None
                    
                    # Test the method
                    target_date = date(2024, 1, 15)
                    result = await client._fetch_raw_data(target_date)
                    
                    # Verify the result structure
                    assert isinstance(result, dict)
                    assert result['stats'] is None
                    assert result['sleep_data'] is not None
                    assert result['activities'] is None
                    assert result['summary'] is not None
                    assert result['training_status'] is None
                    assert result['hrv_payload'] is None

    @pytest.mark.asyncio
    async def test_fetch_raw_data_concurrent_execution(self):
        """Test that data fetching happens concurrently (not sequentially)."""
        from datetime import date
        import time
        
        client = GarminClient()
        
        # Mock the client methods with delays
        with patch.object(client, 'client') as mock_client:
            # Mock the executor with delays to test concurrency
            with patch('asyncio.get_event_loop') as mock_loop:
                async def delayed_executor(func, *args):
                    await asyncio.sleep(0.1)  # 100ms delay
                    return {'test': 'data'}
                
                mock_loop.return_value.run_in_executor = delayed_executor
                
                # Mock _fetch_hrv_data with delay
                with patch.object(client, '_fetch_hrv_data', new_callable=AsyncMock) as mock_hrv:
                    async def delayed_hrv(*args):
                        await asyncio.sleep(0.1)  # 100ms delay
                        return {'hrvSummary': {'lastNightAvg': 45}}
                    
                    mock_hrv.side_effect = delayed_hrv
                    
                    # Test the method and measure time
                    target_date = date(2024, 1, 15)
                    start_time = time.time()
                    result = await client._fetch_raw_data(target_date)
                    end_time = time.time()
                    
                    # If sequential, this would take ~600ms (6 calls * 100ms each)
                    # If concurrent, this should take ~100ms (limited by slowest call)
                    execution_time = end_time - start_time
                    assert execution_time < 0.2  # Should be much less than 600ms
                    
                    # Verify we got all the data
                    assert all(key in result for key in ['stats', 'sleep_data', 'activities', 'summary', 'training_status', 'hrv_payload'])
    
    @pytest.mark.asyncio
    async def test_get_metrics_for_date_range_success(self):
        """Test successful metrics fetching for a date range."""
        client = GarminClient()
        
        # Mock the get_metrics method to return fake data
        with patch.object(client, 'get_metrics', new_callable=AsyncMock) as mock_get_metrics:
            # Create fake metrics for 3 days
            fake_metrics = [
                DailyMetrics(
                    date=date(2024, 1, 15),
                    sleep=SleepMetrics(date=date(2024, 1, 15), sleep_score=85.0),
                    health=HealthMetrics(date=date(2024, 1, 15)),
                    recovery=RecoveryMetrics(date=date(2024, 1, 15)),
                    swimming=SwimmingMetrics(date=date(2024, 1, 15))
                ),
                DailyMetrics(
                    date=date(2024, 1, 16),
                    sleep=SleepMetrics(date=date(2024, 1, 16), sleep_score=90.0),
                    health=HealthMetrics(date=date(2024, 1, 16)),
                    recovery=RecoveryMetrics(date=date(2024, 1, 16)),
                    swimming=SwimmingMetrics(date=date(2024, 1, 16))
                ),
                DailyMetrics(
                    date=date(2024, 1, 17),
                    sleep=SleepMetrics(date=date(2024, 1, 17), sleep_score=88.0),
                    health=HealthMetrics(date=date(2024, 1, 17)),
                    recovery=RecoveryMetrics(date=date(2024, 1, 17)),
                    swimming=SwimmingMetrics(date=date(2024, 1, 17))
                )
            ]
            mock_get_metrics.side_effect = fake_metrics
            
            # Test the date range method
            start_date = date(2024, 1, 15)
            end_date = date(2024, 1, 17)
            result = await client.get_metrics_for_date_range(start_date, end_date, "test@example.com", "password123")
            
            # Verify results
            assert len(result) == 3
            assert result[0].date == date(2024, 1, 15)
            assert result[1].date == date(2024, 1, 16)
            assert result[2].date == date(2024, 1, 17)
            
            # Verify get_metrics was called 3 times
            assert mock_get_metrics.call_count == 3

    @pytest.mark.asyncio
    async def test_get_metrics_for_date_range_no_data(self):
        """Test metrics fetching when no data is returned."""
        client = GarminClient()
        
        # Mock get_metrics to return None (no data)
        with patch.object(client, 'get_metrics', new_callable=AsyncMock) as mock_get_metrics:
            mock_get_metrics.return_value = None
            
            # Test the date range method
            start_date = date(2024, 1, 15)
            end_date = date(2024, 1, 17)
            
            # Should raise an exception
            with pytest.raises(Exception) as exc_info:
                await client.get_metrics_for_date_range(start_date, end_date, "test@example.com", "password123")
            
            assert "No metrics data found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_metrics_for_date_range_single_day(self):
        """Test metrics fetching for a single day."""
        client = GarminClient()
        
        # Mock the get_metrics method to return fake data
        with patch.object(client, 'get_metrics', new_callable=AsyncMock) as mock_get_metrics:
            fake_metric = DailyMetrics(
                date=date(2024, 1, 15),
                sleep=SleepMetrics(date=date(2024, 1, 15), sleep_score=85.0),
                health=HealthMetrics(date=date(2024, 1, 15)),
                recovery=RecoveryMetrics(date=date(2024, 1, 15)),
                swimming=SwimmingMetrics(date=date(2024, 1, 15))
            )
            mock_get_metrics.return_value = fake_metric
            
            # Test the date range method for single day
            start_date = date(2024, 1, 15)
            end_date = date(2024, 1, 15)
            result = await client.get_metrics_for_date_range(start_date, end_date, "test@example.com", "password123")
            
            # Verify results
            assert len(result) == 1
            assert result[0].date == date(2024, 1, 15)
            assert result[0].sleep.sleep_score == 85.0
            
            # Verify get_metrics was called once
            assert mock_get_metrics.call_count == 1

    @pytest.mark.asyncio
    async def test_get_metrics_for_date_range_mixed_data(self):
        """Test metrics fetching when some days have data and others don't."""
        client = GarminClient()
        
        # Mock the get_metrics method to return mixed data
        with patch.object(client, 'get_metrics', new_callable=AsyncMock) as mock_get_metrics:
            # First day has data, second day has no data, third day has data
            fake_metrics = [
                DailyMetrics(
                    date=date(2024, 1, 15),
                    sleep=SleepMetrics(date=date(2024, 1, 15), sleep_score=85.0),
                    health=HealthMetrics(date=date(2024, 1, 15)),
                    recovery=RecoveryMetrics(date=date(2024, 1, 15)),
                    swimming=SwimmingMetrics(date=date(2024, 1, 15))
                ),
                None,  # No data for this day
                DailyMetrics(
                    date=date(2024, 1, 17),
                    sleep=SleepMetrics(date=date(2024, 1, 17), sleep_score=88.0),
                    health=HealthMetrics(date=date(2024, 1, 17)),
                    recovery=RecoveryMetrics(date=date(2024, 1, 17)),
                    swimming=SwimmingMetrics(date=date(2024, 1, 17))
                )
            ]
            mock_get_metrics.side_effect = fake_metrics
            
            # Test the date range method
            start_date = date(2024, 1, 15)
            end_date = date(2024, 1, 17)
            result = await client.get_metrics_for_date_range(start_date, end_date, "test@example.com", "password123")
            
            # Verify results - should only include days with data
            assert len(result) == 2
            assert result[0].date == date(2024, 1, 15)
            assert result[1].date == date(2024, 1, 17)
            
            # Verify get_metrics was called 3 times
            assert mock_get_metrics.call_count == 3
