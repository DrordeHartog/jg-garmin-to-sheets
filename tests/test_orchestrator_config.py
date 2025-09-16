#!/usr/bin/env python3
"""
Test ETL Orchestrator with configuration.
"""

import sys
import os
from pathlib import Path

def test_orchestrator_config():
    """Test ETL Orchestrator configuration."""
    print("Testing ETL Orchestrator configuration...")
    
    try:
        # Add project root to path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        # Import required modules
        from src.etl.orchestration.orchestrator import ETLOrchestrator
        from src.etl.orchestration.config import OrchestratorConfig
        
        # Test 1: Default config
        print("  ✓ Testing default config...")
        orchestrator1 = ETLOrchestrator()
        assert orchestrator1.cache_dir == Path("data/cache"), "Default cache dir should be data/cache"
        
        # Test 2: Custom config
        print("  ✓ Testing custom config...")
        custom_config = OrchestratorConfig(cache_dir="custom/cache/path")
        orchestrator2 = ETLOrchestrator(custom_config)
        assert orchestrator2.cache_dir == Path("custom/cache/path"), "Custom cache dir should be used"
        
        # Test 3: Config properties
        print("  ✓ Testing config properties...")
        assert orchestrator1.config.database_path == "data/health_data.db", "Default database path should be set"
        assert orchestrator1.config.max_concurrent_jobs == 3, "Default max concurrent jobs should be 3"
        
        # Test 4: Cache manager integration
        print("  ✓ Testing cache manager integration...")
        assert orchestrator1.cache_manager is not None, "Cache manager should be initialized"
        assert orchestrator1.cache_manager.cache_dir == orchestrator1.cache_dir, "Cache manager should use same cache dir"
        
        print("\n✅ All orchestrator config tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestrator config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ETL Orchestrator Config Test")
    print("=" * 50)
    
    success = test_orchestrator_config()
    
    if success:
        print("\n🎉 ETL Orchestrator configuration is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 ETL Orchestrator config test failed.")
        sys.exit(1)
