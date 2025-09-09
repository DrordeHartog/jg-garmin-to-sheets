#!/usr/bin/env python3
"""
Script to test Garmin API connectivity and rate limiting status.

This script will:
1. Test authentication
2. Try to fetch data for a single recent date
3. Check if rate limiting has been lifted
4. Analyze API response patterns
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.garmin_client import GarminClient
from src.utils.logging_config import setup_custom_logging
import logging

logger = logging.getLogger(__name__)

async def test_api_connectivity():
    """Test Garmin API connectivity and rate limiting status."""
    
    print("🔍 Testing Garmin API Connectivity")
    print("=" * 50)
    
    # Setup logging
    setup_custom_logging(level="INFO", output="console")
    
    # Get credentials from user
    print("🔐 Garmin Credentials Required")
    email = input("Enter your Garmin email: ").strip()
    password = input("Enter your Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    # Initialize client
    garmin_client = GarminClient()
    
    # Test dates (try recent dates)
    test_dates = [
        date.today(),
        date.today() - timedelta(days=1),
        date.today() - timedelta(days=2),
        date.today() - timedelta(days=3)
    ]
    
    print(f"\n📅 Testing API with {len(test_dates)} recent dates...")
    
    for i, test_date in enumerate(test_dates, 1):
        print(f"\n🔄 Test {i}/{len(test_dates)}: {test_date}")
        
        try:
            # Authenticate
            print("  🔐 Authenticating...")
            await garmin_client.authenticate(email, password)
            print("  ✅ Authentication successful")
            
            # Fetch raw data
            print("  📊 Fetching raw data...")
            raw_data = await garmin_client._fetch_raw_data(test_date)
            
            # Analyze response
            if raw_data:
                print("  ✅ Data fetched successfully")
                
                # Check what data is available
                hrv_data = raw_data.get('hrv_payload')
                sleep_data = raw_data.get('sleep_data')
                summary_data = raw_data.get('summary')
                
                print(f"  📈 Data availability:")
                print(f"    - HRV data: {'✅' if hrv_data else '❌'}")
                print(f"    - Sleep data: {'✅' if sleep_data else '❌'}")
                print(f"    - Summary data: {'✅' if summary_data else '❌'}")
                
                # Show sample data if available
                if hrv_data and hrv_data.get('hrvSummary'):
                    hrv_summary = hrv_data['hrvSummary']
                    print(f"    - HRV status: {hrv_summary.get('status', 'N/A')}")
                    print(f"    - HRV avg: {hrv_summary.get('lastNightAvg', 'N/A')}")
                
                if sleep_data and sleep_data.get('dailySleepDTO'):
                    sleep_dto = sleep_data['dailySleepDTO']
                    sleep_score = sleep_dto.get('sleepScores', {}).get('overall', {}).get('value')
                    sleep_time = sleep_dto.get('sleepTimeSeconds')
                    print(f"    - Sleep score: {sleep_score}")
                    print(f"    - Sleep time: {sleep_time} seconds" if sleep_time else "    - Sleep time: N/A")
                
                if summary_data:
                    stress = summary_data.get('averageStressLevel')
                    hr = summary_data.get('restingHeartRate')
                    print(f"    - Stress level: {stress}")
                    print(f"    - Resting HR: {hr}")
                
            else:
                print("  ⚠️  No data returned (empty response)")
            
            # Small delay between requests
            await asyncio.sleep(1)
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error: {error_msg}")
            
            # Check if it's a rate limiting error
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print("  🚫 Rate limiting detected - API is still restricted")
                print("  💡 Recommendation: Wait longer before retrying")
            elif "Authentication failed" in error_msg:
                print("  🔐 Authentication issue - check credentials")
            else:
                print(f"  🔍 Other error: {error_msg}")
            
            # If we hit rate limiting, stop testing
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print("\n⏹️  Stopping tests due to rate limiting")
                break
    
    print(f"\n📊 API Connectivity Test Summary:")
    print(f"✅ Tests completed")
    print(f"💡 If rate limiting persists, consider:")
    print(f"   - Waiting 24+ hours before retrying")
    print(f"   - Implementing exponential backoff")
    print(f"   - Reducing request frequency")
    print(f"   - Using different authentication method")

if __name__ == "__main__":
    asyncio.run(test_api_connectivity())
