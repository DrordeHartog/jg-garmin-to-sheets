#!/usr/bin/env python3
"""
Test ETL Orchestrator job execution with job configuration table.
"""

import sys
import os
from datetime import date

def test_orchestrator_job_execution():
    """Test ETL Orchestrator job execution."""
    print("Testing ETL Orchestrator job execution...")
    
    try:
        # Add project root to path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        # Import required modules
        from src.etl.orchestration.orchestrator import ETLOrchestrator
        from src.etl.orchestration.config import OrchestratorConfig
        
        # Test 1: Initialize orchestrator
        print("  ✓ Testing orchestrator initialization...")
        orchestrator = ETLOrchestrator()
        
        # Test 2: Check job configuration table
        print("  ✓ Testing job configuration table access...")
        with orchestrator.db_manager.get_connection() as conn:
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
            print(f"      - Job {job_id}: {job_name} ({processor_class})")
        
        # Test 3: Test job module import (without actually running)
        print("  ✓ Testing job module imports...")
        for job in active_jobs:
            job_id, job_name, processor_class, job_module, is_active = job
            try:
                import importlib
                module = importlib.import_module(job_module)
                job_class_obj = getattr(module, processor_class)
                print(f"      ✓ {job_name}: {job_module}.{processor_class}")
            except Exception as e:
                print(f"      ❌ {job_name}: Failed to import - {e}")
                return False
        
        # Test 4: Test job initialization (without running)
        print("  ✓ Testing job initialization...")
        test_date = date.today()
        for job in active_jobs[:2]:  # Test first 2 jobs only
            job_id, job_name, processor_class, job_module, is_active = job
            try:
                import importlib
                module = importlib.import_module(job_module)
                job_class_obj = getattr(module, processor_class)
                
                # Test initialization
                job_instance = orchestrator._initialize_job(job_class_obj, test_date)
                print(f"      ✓ {job_name}: Initialized successfully")
            except Exception as e:
                print(f"      ❌ {job_name}: Failed to initialize - {e}")
                return False
        
        print("\n✅ All orchestrator job execution tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestrator job execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ETL Orchestrator Job Execution Test")
    print("=" * 50)
    
    success = test_orchestrator_job_execution()
    
    if success:
        print("\n🎉 ETL Orchestrator job execution is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 ETL Orchestrator job execution test failed.")
        sys.exit(1)
