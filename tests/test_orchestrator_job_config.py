#!/usr/bin/env python3
"""
Test ETL Orchestrator job configuration table access.
"""

import sys
import os
from datetime import date

def test_orchestrator_job_config():
    """Test ETL Orchestrator job configuration table access."""
    print("Testing ETL Orchestrator job configuration...")
    
    try:
        # Add project root to path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        # Import database manager directly
        from src.database.database_manager import DatabaseManager
        from src.etl.orchestration.config import OrchestratorConfig
        
        # Test 1: Initialize database manager
        print("  ✓ Testing database manager initialization...")
        config = OrchestratorConfig()
        db_manager = DatabaseManager(config.database_path)
        
        # Test 2: Check job configuration table
        print("  ✓ Testing job configuration table access...")
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id, job_name, processor_class, job_module, is_active 
                FROM etl_job_config 
                WHERE is_active = 1 
                ORDER BY job_id
            """)
            active_jobs = cursor.fetchall()
            
        print(f"    Found {len(active_jobs)} active jobs:")
        for job in active_jobs:
            job_id, job_name, processor_class, job_module, is_active = job
            print(f"      - Job {job_id}: {job_name}")
            print(f"        Class: {processor_class}")
            print(f"        Module: {job_module}")
        
        # Test 3: Test job module import (without actually running)
        print("  ✓ Testing job module imports...")
        import importlib
        for job in active_jobs:
            job_id, job_name, processor_class, job_module, is_active = job
            try:
                module = importlib.import_module(job_module)
                job_class_obj = getattr(module, processor_class)
                print(f"      ✓ {job_name}: {job_module}.{processor_class}")
            except Exception as e:
                print(f"      ❌ {job_name}: Failed to import - {e}")
                return False
        
        # Test 4: Test job configuration query (like orchestrator does)
        print("  ✓ Testing job configuration query...")
        test_job_id = active_jobs[0][0]  # Use first job ID
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_name, processor_class, job_module, description 
                FROM etl_job_config 
                WHERE job_id = ? AND is_active = 1
            """, (test_job_id,))
            job_config = cursor.fetchone()
            
        if job_config:
            job_name, processor_class, job_module, description = job_config
            print(f"      ✓ Job {test_job_id}: {job_name} - {description}")
            print(f"        Class: {processor_class}")
            print(f"        Module: {job_module}")
        else:
            print(f"      ❌ Job {test_job_id}: Not found")
            return False
        
        print("\n✅ All orchestrator job configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestrator job configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ETL Orchestrator Job Configuration Test")
    print("=" * 50)
    
    success = test_orchestrator_job_config()
    
    if success:
        print("\n🎉 ETL Orchestrator job configuration is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 ETL Orchestrator job configuration test failed.")
        sys.exit(1)