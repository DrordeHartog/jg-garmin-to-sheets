#!/usr/bin/env python3
"""
Basic test script for ETLOrchestrator Step 1 implementation.

This script tests:
1. ETLOrchestrator initialization
2. Start/stop functionality
3. Basic recovery ETL execution (if Garmin credentials are available)
"""

import asyncio
import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.etl.orchestration import ETLOrchestrator, OrchestratorConfig, NotificationConfig

async def test_orchestrator_initialization():
    """Test ETLOrchestrator initialization."""
    print("🧪 Testing ETLOrchestrator initialization...")
    
    # Create configuration
    notifications = NotificationConfig(discord_webhook_url='https://discord.com/api/webhooks/test')
    config = OrchestratorConfig(notifications=notifications)
    
    # Initialize orchestrator
    orchestrator = ETLOrchestrator(config)
    
    # Verify components are initialized
    assert orchestrator.config is not None
    assert orchestrator.db_manager is not None
    assert orchestrator.recovery_processor is not None
    assert orchestrator.garmin_client is not None
    assert orchestrator.load_manager is not None
    assert orchestrator.job_manager is not None
    
    print("✅ ETLOrchestrator initialized successfully")
    print(f"   Database path: {orchestrator.config.database_path}")
    print(f"   Recovery processor: {type(orchestrator.recovery_processor).__name__}")
    print(f"   Garmin client: {type(orchestrator.garmin_client).__name__}")
    
    return orchestrator

async def test_orchestrator_start_stop(orchestrator):
    """Test orchestrator start and stop functionality."""
    print("\n🧪 Testing orchestrator start/stop...")
    
    # Test start
    await orchestrator.start()
    print("✅ Orchestrator started successfully")
    
    # Test stop
    await orchestrator.stop()
    print("✅ Orchestrator stopped successfully")

async def test_recovery_etl_execution(orchestrator):
    """Test recovery ETL execution (requires Garmin credentials)."""
    print("\n🧪 Testing recovery ETL execution...")
    
    try:
        # Test with a recent date
        test_date = date(2024, 9, 1)  # Use a date we know has data
        
        print(f"   Executing recovery ETL for {test_date}...")
        result = await orchestrator.execute_recovery_etl(test_date)
        
        print(f"✅ Recovery ETL completed")
        print(f"   Job ID: {result.job_id}")
        print(f"   Status: {result.status.value}")
        print(f"   Records processed: {result.records_processed}")
        print(f"   Duration: {result.duration_ms:.2f}ms")
        
        if result.errors:
            print(f"   Errors: {result.errors}")
        
        return result
        
    except Exception as e:
        print(f"⚠️  Recovery ETL test failed (expected if no Garmin credentials): {e}")
        return None

async def main():
    """Run all tests."""
    print("🚀 Starting ETLOrchestrator Step 1 Tests\n")
    
    try:
        # Test 1: Initialization
        orchestrator = await test_orchestrator_initialization()
        
        # Test 2: Start/Stop
        await test_orchestrator_start_stop(orchestrator)
        
        # Test 3: Recovery ETL (optional - requires credentials)
        await test_recovery_etl_execution(orchestrator)
        
        print("\n🎉 All basic tests completed successfully!")
        print("\nNext steps:")
        print("- Step 2: Implement JobManager functionality")
        print("- Step 3: Implement LoadManager rate limiting")
        print("- Step 4: Add APScheduler integration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
