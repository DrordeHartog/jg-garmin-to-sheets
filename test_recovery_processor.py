#!/usr/bin/env python3
"""
Test script for RecoveryProcessor with proper ETL flow.
Tests the new architecture where orchestrator fetches raw data once and passes it to processors.
"""

import sys
import os
import asyncio
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.etl.orchestration.orchestrator import ETLOrchestrator
from src.etl.orchestration.config import OrchestratorConfig, NotificationConfig, RateLimit


async def test_recovery_processor_flow():
    """Test the new ETL flow: authenticate -> fetch raw data -> process recovery data."""
    
    print("🧪 Testing RecoveryProcessor with new ETL flow...")
    
    # Initialize orchestrator
    config = OrchestratorConfig(
        rate_limits={"garmin": RateLimit(requests_per_minute=10, requests_per_hour=100)},
        notifications=NotificationConfig(discord_webhook_url="dummy_url"),
        database_path="data/health_data.db"
    )
    
    orchestrator = ETLOrchestrator(config)
    
    try:
        # Start orchestrator
        print("1. Starting orchestrator...")
        await orchestrator.start()
        print("✅ Orchestrator started successfully")
        
        # Test authentication (you'll need to provide real credentials)
        print("\n2. Testing authentication...")
        email = input("Enter Garmin email: ").strip()
        password = input("Enter Garmin password: ").strip()
        
        auth_success = await orchestrator.authenticate_garmin(email, password)
        if not auth_success:
            print("❌ Authentication failed")
            return
        print("✅ Authentication successful")
        
        # Test raw data fetching
        print("\n3. Testing raw data fetching...")
        target_date = date.today()
        raw_data = await orchestrator.fetch_and_cache_raw_data(target_date)
        
        if not raw_data:
            print("❌ No raw data fetched")
            return
        print(f"✅ Raw data fetched successfully. Keys: {list(raw_data.keys())}")
        
        # Test recovery ETL processing
        print("\n4. Testing recovery ETL processing...")
        result = await orchestrator.execute_recovery_etl(raw_data, target_date)
        
        if result.status.value == "completed":
            print(f"✅ Recovery ETL completed successfully!")
            print(f"   Records processed: {result.records_processed}")
            print(f"   Duration: {result.duration_ms:.2f}ms")
        else:
            print(f"❌ Recovery ETL failed: {result.errors}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Stop orchestrator
        print("\n5. Stopping orchestrator...")
        await orchestrator.stop()
        print("✅ Orchestrator stopped")


if __name__ == "__main__":
    asyncio.run(test_recovery_processor_flow())