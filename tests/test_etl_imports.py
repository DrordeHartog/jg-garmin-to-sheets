#!/usr/bin/env python3
"""
Basic test to verify all ETL imports work correctly.
"""

import sys
import traceback
from datetime import date

def test_imports():
    """Test all ETL module imports."""
    print("Testing ETL module imports...")
    
    try:
        # Test main ETL module
        print("  ✓ Importing src.etl...")
        import src.etl
        
        # Test base job
        print("  ✓ Importing base job...")
        from src.etl.jobs.base_job import BaseETLJob
        
        # Test API to cache job
        print("  ✓ Importing API to cache job...")
        from src.etl.jobs.api_to_cache.garmin_api_to_cache_job import GarminAPIToCacheJob
        
        # Test cache to raw jobs
        print("  ✓ Importing cache to raw jobs...")
        from src.etl.jobs.cache_to_raw.recovery_job import RecoveryCacheToRawJob
        from src.etl.jobs.cache_to_raw.swimming_sessions_job import SwimmingSessionsCacheToRawJob
        from src.etl.jobs.cache_to_raw.swimming_laps_job import SwimmingLapsCacheToRawJob
        from src.etl.jobs.cache_to_raw.swimming_intervals_job import SwimmingIntervalsCacheToRawJob
        
        # Test raw to processed jobs
        print("  ✓ Importing raw to processed jobs...")
        from src.etl.jobs.raw_to_processed.processed_swimming_sessions_job import ProcessedSwimmingSessionsJob
        
        # Test services
        print("  ✓ Importing services...")
        from src.etl.services.garmin_client import GarminClient
        
        # Test utilities
        print("  ✓ Importing utilities...")
        from src.etl.utils.cache_manager import CacheManager
        from src.etl.utils.transformers import transform_garmin_data
        from src.etl.utils.validators import validate_job_config
        
        # Test orchestrator
        print("  ✓ Importing orchestrator...")
        from src.etl.orchestration.orchestrator import ETLOrchestrator
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_basic_instantiation():
    """Test basic instantiation of key classes."""
    print("\nTesting basic instantiation...")
    
    try:
        # Test cache manager
        print("  ✓ Testing CacheManager...")
        from pathlib import Path
        from src.etl.utils.cache_manager import CacheManager
        cache_manager = CacheManager(Path("test_cache"))
        
        # Test Garmin client
        print("  ✓ Testing GarminClient...")
        from src.etl.services.garmin_client import GarminClient
        garmin_client = GarminClient()
        
        # Test orchestrator
        print("  ✓ Testing ETLOrchestrator...")
        from src.etl.orchestration.orchestrator import ETLOrchestrator
        orchestrator = ETLOrchestrator()
        
        # Test job instantiation
        print("  ✓ Testing job instantiation...")
        from src.etl.jobs.api_to_cache.garmin_api_to_cache_job import GarminAPIToCacheJob
        job = GarminAPIToCacheJob(date.today(), garmin_client, cache_manager)
        
        print("\n✅ All instantiation successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Instantiation error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ETL Import Test")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_basic_instantiation()
    
    if success:
        print("\n🎉 All tests passed! ETL structure is ready.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        sys.exit(1)
