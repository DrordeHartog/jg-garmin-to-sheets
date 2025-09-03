"""Basic tests to validate the refactoring."""

import pytest
from pathlib import Path

def test_imports_work():
    """Test that basic imports work after refactoring."""
    try:
        from src.core import GarminClient
        from src.exceptions import MFARequiredException  # ← Import from root level
        assert True, "Core modules imported successfully"
    except ImportError as e:
        assert False, f"Import failed: {e}"

def test_models_work():
    """Test that data models can be created."""
    try:
        from src.core.models import SwimmingMetrics
        from datetime import date
        
        metrics = SwimmingMetrics(date=date(2024, 1, 15))
        assert metrics.date == date(2024, 1, 15)
        assert True, "Models work correctly"
    except Exception as e:
        assert False, f"Models failed: {e}"

def test_basic_structure():
    """Quick check that key files exist."""
    key_files = [
        'src/core/__init__.py',
        'src/core/models.py',
        'src/core/garmin_client.py',
        'src/exceptions.py'  # ← Add this check
    ]
    
    for file_path in key_files:
        assert Path(file_path).exists(), f"File {file_path} should exist"