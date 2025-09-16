#!/usr/bin/env python3
"""
Test CacheManager utility.
"""

import sys
import tempfile
import shutil
from datetime import date
from pathlib import Path

def test_cache_manager():
    """Test CacheManager functionality."""
    print("Testing CacheManager...")
    
    try:
        # Import CacheManager
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from src.etl.utils.cache_manager import CacheManager
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "test_cache"
            cache_manager = CacheManager(cache_dir, max_size_mb=1)  # 1MB limit for testing
            
            # Test data
            test_date = date(2024, 1, 15)
            test_data = {
                "stats": {"weight": 70.5, "body_fat": 15.2},
                "activities": [{"id": 1, "type": "swimming", "distance": 1000}],
                "sleep_data": {"duration": 8.5, "quality": "good"}
            }
            
            # Test 1: Save to cache
            print("  ✓ Testing save_to_cache...")
            cache_manager.save_to_cache(test_date, test_data)
            
            # Test 2: Load from cache
            print("  ✓ Testing load_from_cache...")
            loaded_data = cache_manager.load_from_cache(test_date)
            assert loaded_data == test_data, "Loaded data doesn't match saved data"
            
            # Test 3: Get cache file path
            print("  ✓ Testing get_cache_file_path...")
            cache_file = cache_manager.get_cache_file_path(test_date)
            assert cache_file.exists(), "Cache file should exist"
            assert cache_file.name == "2024-01-15.json", "Cache file name should match date"
            
            # Test 4: Get cache size
            print("  ✓ Testing get_cache_size_mb...")
            cache_size = cache_manager.get_cache_size_mb()
            assert cache_size > 0, "Cache size should be greater than 0"
            
            # Test 5: Get cached files
            print("  ✓ Testing get_cached_files...")
            cached_files = cache_manager.get_cached_files()
            assert len(cached_files) == 1, "Should have 1 cached file"
            
            # Test 6: Load non-existent cache
            print("  ✓ Testing load non-existent cache...")
            non_existent_date = date(2024, 1, 16)
            no_data = cache_manager.load_from_cache(non_existent_date)
            assert no_data is None, "Non-existent cache should return None"
            
            print("\n✅ All CacheManager tests passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ CacheManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("CacheManager Test")
    print("=" * 50)
    
    success = test_cache_manager()
    
    if success:
        print("\n🎉 CacheManager is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 CacheManager test failed.")
        sys.exit(1)
