"""
Sprint 1 Import Tests

Tests that verify all import paths fixed during Sprint 1 work correctly.
This ensures the restructuring from src.* imports to relative imports was successful.

Sprint 1 fixes:
- CLI commands: Changed src.etl → ..etl
- Orchestrator: Changed database.database_manager → ...database.SQLiteManager
- Jobs: Changed shared.models → ....shared.models
- Garmin client: Changed src.exceptions → ...exceptions
- Monitoring: Changed .logging_config → ..shared.logging_config

All tests verify that imports work without ModuleNotFoundError or ImportError.
"""

import pytest


def test_cli_module_imports():
    """Test that CLI module imports work with relative imports.

    Sprint 1 fix: Changed from 'from src.etl...' to 'from ..etl...'
    Files fixed:
    - src/garmingo/cli/etl_commands.py (lines 10-12)
    """
    from src.garmingo.cli.etl_commands import ETLCommands, main

    assert callable(main), "main should be a callable function"
    assert ETLCommands is not None, "ETLCommands class should be importable"


def test_orchestrator_imports():
    """Test that orchestrator imports work with fixed paths.

    Sprint 1 fix: Changed from 'database.database_manager' to '...database.SQLiteManager'
    Files fixed:
    - src/garmingo/etl/orchestration/orchestrator.py (line 37)
    """
    from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator

    assert ETLOrchestrator is not None, "ETLOrchestrator class should be importable"


def test_config_classes_import():
    """Test that all config classes import correctly.

    Sprint 1 addition: Added NotificationConfig class
    Files modified:
    - src/garmingo/etl/orchestration/config.py (added NotificationConfig dataclass)
    """
    from src.garmingo.etl.orchestration.config import (
        OrchestratorConfig,
        NotificationConfig,
        JobStatus,
        JobResult,
        JobConfig,
        RateLimit
    )

    assert OrchestratorConfig is not None, "OrchestratorConfig should be importable"
    assert NotificationConfig is not None, "NotificationConfig should be importable"
    assert JobStatus is not None, "JobStatus enum should be importable"
    assert JobResult is not None, "JobResult should be importable"
    assert JobConfig is not None, "JobConfig should be importable"
    assert RateLimit is not None, "RateLimit should be importable"


def test_sqlite_manager_imports():
    """Test that SQLiteManager imports correctly.

    Sprint 1 fix: Changed references from DatabaseManager to SQLiteManager
    Files fixed:
    - src/garmingo/cli/etl_commands.py (lines 12, 38, 86)
    - src/garmingo/etl/orchestration/orchestrator.py (line 37)
    """
    from src.garmingo.database.SQLiteManager import SQLiteManager

    assert SQLiteManager is not None, "SQLiteManager should be importable"


def test_sqlite_client_imports():
    """Test that SQLiteClient imports from adapters (not non-existent services).

    Sprint 1 fix: Changed from '..services.database_client' to '..adapters.SQLiteClient'
    Files fixed:
    - src/garmingo/etl/orchestration/orchestrator.py (line 38)
    - src/garmingo/etl/jobs/cache_to_raw/swimming_laps_job.py (line 12)
    """
    from src.garmingo.etl.adapters.SQLiteClient import SQLiteClient

    assert SQLiteClient is not None, "SQLiteClient should be importable from adapters"


def test_job_imports():
    """Test that swimming_laps_job imports work with fixed paths.

    Sprint 1 fixes:
    - Changed 'from shared.models' to 'from ....shared.models'
    - Changed DatabaseClient to SQLiteClient
    Files fixed:
    - src/garmingo/etl/jobs/cache_to_raw/swimming_laps_job.py (lines 12, 14)
    """
    from src.garmingo.etl.jobs.cache_to_raw.swimming_laps_job import Swimming_Laps_Job

    assert Swimming_Laps_Job is not None, "Swimming_Laps_Job should be importable"


def test_monitoring_imports():
    """Test that monitoring module imports work.

    Sprint 1 fix: Commented out non-existent StructuredLogger/LogEntry imports
    Files fixed:
    - src/garmingo/monitoring/__init__.py (line 8)
    """
    from src.garmingo.monitoring import DiscordNotifier, MetricsCollector

    assert DiscordNotifier is not None, "DiscordNotifier should be importable"
    assert MetricsCollector is not None, "MetricsCollector should be importable"


def test_garmin_client_exception_import():
    """Test that garmin_client exception import works.

    Sprint 1 fix: Changed 'from src.exceptions' to 'from ...exceptions'
    Files fixed:
    - src/garmingo/ingestion/clients/garmin_client.py (line 10)
    """
    from src.garmingo.ingestion.clients.garmin_client import GarminClient
    from src.garmingo.exceptions import MFARequiredException

    assert GarminClient is not None, "GarminClient should be importable"
    assert MFARequiredException is not None, "MFARequiredException should be importable"


class TestImportChain:
    """Test that the full import chain works from CLI down to database."""

    def test_cli_to_orchestrator_chain(self):
        """Test import chain: CLI → Orchestrator → Config."""
        from src.garmingo.cli.etl_commands import ETLCommands
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator
        from src.garmingo.etl.orchestration.config import OrchestratorConfig, NotificationConfig

        # All classes should be importable in sequence
        assert all([ETLCommands, ETLOrchestrator, OrchestratorConfig, NotificationConfig])

    def test_orchestrator_to_database_chain(self):
        """Test import chain: Orchestrator → SQLiteClient → SQLiteManager."""
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator
        from src.garmingo.etl.adapters.SQLiteClient import SQLiteClient
        from src.garmingo.database.SQLiteManager import SQLiteManager

        # All classes should be importable in sequence
        assert all([ETLOrchestrator, SQLiteClient, SQLiteManager])

    def test_jobs_to_models_chain(self):
        """Test import chain: Jobs → Models."""
        from src.garmingo.etl.jobs.cache_to_raw.swimming_laps_job import Swimming_Laps_Job
        from src.garmingo.shared.models import SwimmingLap

        # Both should be importable
        assert all([Swimming_Laps_Job, SwimmingLap])
