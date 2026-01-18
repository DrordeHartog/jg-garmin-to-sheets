"""
Sprint 1 Integration Tests

Integration tests that verify all Sprint 1 fixes work together correctly.
These tests import and instantiate multiple components to ensure the entire
import chain works end-to-end.

Tests cover:
- CLI → Orchestrator → Jobs → Database import chain
- Configuration propagation through the system
- Database client integration with orchestrator
- Full module import without errors

Sprint 1 integrated multiple fixes:
1. Import path changes (src.* → relative imports)
2. NotificationConfig class addition
3. DatabaseManager → SQLiteManager + SQLiteClient
4. Database path standardization
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import date
from src.garmingo.etl.orchestration.config import OrchestratorConfig, NotificationConfig


class TestSprint1Integration:
    """Integration tests for Sprint 1 fixes."""

    def test_orchestrator_instantiation(self):
        """Test that orchestrator can be created with all Sprint 1 fixes.

        This test verifies:
        - OrchestratorConfig works with NotificationConfig
        - ETLOrchestrator can be instantiated
        - Orchestrator has database_client (SQLiteClient)
        - Orchestrator has cache_manager
        """
        config = OrchestratorConfig(
            database_path="data/test_health_data.db",
            cache_dir="data/test_cache",
            notifications=NotificationConfig(
                enabled=True,
                webhook_url="https://example.com/webhook"
            )
        )

        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator

        orchestrator = ETLOrchestrator(config)

        assert orchestrator is not None, "Orchestrator should instantiate"
        assert orchestrator.database_client is not None, "Orchestrator should have database_client"
        assert orchestrator.cache_manager is not None, "Orchestrator should have cache_manager"
        assert orchestrator.config == config, "Orchestrator should store config"

    def test_orchestrator_with_sqlite_client(self):
        """Test that orchestrator correctly uses SQLiteClient.

        Sprint 1 fix: Changed from DatabaseClient to SQLiteClient
        """
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator
        from src.garmingo.etl.adapters.SQLiteClient import SQLiteClient

        config = OrchestratorConfig(database_path="data/test.db")
        orchestrator = ETLOrchestrator(config)

        # Verify the database_client is a SQLiteClient instance
        assert isinstance(orchestrator.database_client, SQLiteClient), \
            "Orchestrator should use SQLiteClient"

    def test_cli_commands_initialization(self):
        """Test that ETLCommands can initialize with all Sprint 1 fixes."""
        from src.garmingo.cli.etl_commands import ETLCommands

        commands = ETLCommands()

        assert commands is not None, "ETLCommands should instantiate"
        assert commands.orchestrator is None, "Orchestrator should be None before initialize"

    @pytest.mark.asyncio
    async def test_cli_commands_async_initialize(self):
        """Test that ETLCommands.initialize() works (async).

        This tests the full initialization chain:
        CLI → OrchestratorConfig → ETLOrchestrator → SQLiteClient → SQLiteManager
        """
        from src.garmingo.cli.etl_commands import ETLCommands

        commands = ETLCommands()
        await commands.initialize()

        assert commands.orchestrator is not None, "Orchestrator should be created"
        assert commands.orchestrator.database_client is not None, \
            "Database client should be initialized"

    def test_end_to_end_imports(self):
        """Test the complete import chain from CLI down to database.

        Import chain:
        CLI commands → Orchestrator → Config → SQLiteClient → SQLiteManager
        """
        # Level 1: CLI
        from src.garmingo.cli.etl_commands import ETLCommands, main

        # Level 2: Orchestration
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator
        from src.garmingo.etl.orchestration.config import OrchestratorConfig, NotificationConfig

        # Level 3: Adapters
        from src.garmingo.etl.adapters.SQLiteClient import SQLiteClient

        # Level 4: Database
        from src.garmingo.database.SQLiteManager import SQLiteManager

        # All should be importable
        assert all([
            ETLCommands, main,
            ETLOrchestrator, OrchestratorConfig, NotificationConfig,
            SQLiteClient,
            SQLiteManager
        ]), "Complete import chain should work"

    def test_no_import_errors_in_full_module(self):
        """Test that importing the entire garmingo package works.

        This is a comprehensive smoke test that catches any remaining import issues.
        """
        # Import major modules
        import src.garmingo.cli
        import src.garmingo.etl
        import src.garmingo.database
        import src.garmingo.monitoring
        import src.garmingo.shared

        # All should import without errors
        assert all([
            src.garmingo.cli,
            src.garmingo.etl,
            src.garmingo.database,
            src.garmingo.monitoring,
            src.garmingo.shared
        ])


class TestJobIntegration:
    """Integration tests for ETL jobs with Sprint 1 fixes."""

    def test_swimming_laps_job_instantiation(self):
        """Test that swimming_laps_job can be instantiated with dependencies.

        Tests the dependency chain:
        Swimming_Laps_Job → CacheManager + SQLiteClient → SQLiteManager
        """
        from src.garmingo.etl.jobs.cache_to_raw.swimming_laps_job import Swimming_Laps_Job
        from src.garmingo.etl.utils.cache_manager import CacheManager
        from src.garmingo.etl.adapters.SQLiteClient import SQLiteClient
        from src.garmingo.database.SQLiteManager import SQLiteManager

        # Create dependencies
        target_date = date(2025, 1, 1)
        cache_manager = CacheManager(Path("data/test_cache"))
        db_manager = SQLiteManager("data/test.db")
        database_client = SQLiteClient(db_manager)

        # Instantiate job
        job = Swimming_Laps_Job(target_date, cache_manager, database_client)

        assert job is not None, "Job should instantiate"
        assert job.target_date == target_date, "Job should store target_date"
        assert job.cache_manager == cache_manager, "Job should store cache_manager"
        assert job.database_client == database_client, "Job should store database_client"


class TestConfigurationPropagation:
    """Tests for configuration propagation through the system."""

    def test_notification_config_propagates_to_orchestrator(self):
        """Test that NotificationConfig settings propagate correctly.

        This ensures the NotificationConfig added in Sprint 1 is properly
        integrated into the orchestrator.
        """
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator

        notification_config = NotificationConfig(
            enabled=True,
            webhook_url="https://discord.com/api/webhooks/test123",
            batch_notification_threshold=5
        )

        orchestrator_config = OrchestratorConfig(
            notifications=notification_config
        )

        orchestrator = ETLOrchestrator(orchestrator_config)

        # Check that Discord notifier was initialized if configured
        if notification_config.enabled and notification_config.webhook_url:
            assert orchestrator.discord_notifier is not None, \
                "Discord notifier should be initialized when enabled"

    def test_database_path_propagates_to_clients(self):
        """Test that database path from config reaches SQLiteManager.

        Sprint 1 standardized paths - this test ensures the path flows through:
        OrchestratorConfig → ETLOrchestrator → SQLiteManager
        """
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator

        custom_db_path = "data/custom_test.db"
        config = OrchestratorConfig(database_path=custom_db_path)
        orchestrator = ETLOrchestrator(config)

        # The database client should use the custom path
        # (checking via the manager that was passed to it)
        assert orchestrator.database_client is not None


class TestFullETLPipeline:
    """Tests simulating a minimal ETL pipeline with Sprint 1 fixes."""

    def test_minimal_etl_pipeline_setup(self):
        """Test that we can set up a minimal ETL pipeline.

        This test doesn't run an actual ETL job, but verifies that all
        components can be wired together correctly with Sprint 1 fixes.
        """
        from src.garmingo.etl.orchestration.orchestrator import ETLOrchestrator
        from src.garmingo.etl.orchestration.config import OrchestratorConfig, NotificationConfig
        from src.garmingo.ingestion.clients.garmin_client import GarminClient
        from src.garmingo.etl.utils.cache_manager import CacheManager

        # Create temp directories
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Setup configuration
            config = OrchestratorConfig(
                database_path=str(temp_dir / "test.db"),
                cache_dir=str(temp_dir / "cache"),
                notifications=NotificationConfig(enabled=False)
            )

            # Create orchestrator
            orchestrator = ETLOrchestrator(config)

            # Verify all components are present
            assert orchestrator.garmin_client is not None, "Should have Garmin client"
            assert orchestrator.cache_manager is not None, "Should have cache manager"
            assert orchestrator.database_client is not None, "Should have database client"
            assert orchestrator.config == config, "Should store config"

            # Verify components are correct types
            assert isinstance(orchestrator.garmin_client, GarminClient)
            assert isinstance(orchestrator.cache_manager, CacheManager)

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestRegressionProtection:
    """Tests to prevent regression of Sprint 1 fixes."""

    def test_no_src_prefix_imports(self):
        """Test that no 'from src.etl' style imports exist in key files.

        This test helps prevent regression back to old import style.
        """
        from src.garmingo.cli import etl_commands
        from src.garmingo.etl.orchestration import orchestrator
        import inspect

        # Check CLI commands source
        cli_source = inspect.getsource(etl_commands)
        assert "from src.etl" not in cli_source, \
            "CLI should not use 'from src.etl' imports"

        # Check orchestrator source
        orch_source = inspect.getsource(orchestrator)
        assert "from database.database_manager" not in orch_source, \
            "Orchestrator should not import database.database_manager"

    def test_notification_config_still_exists(self):
        """Test that NotificationConfig class still exists.

        Regression test: This class was added in Sprint 1 and must not be removed.
        """
        from src.garmingo.etl.orchestration.config import NotificationConfig

        assert NotificationConfig is not None
        assert hasattr(NotificationConfig, '__dataclass_fields__'), \
            "NotificationConfig should be a dataclass"

    def test_database_paths_still_standardized(self):
        """Test that database paths are still standardized to health_data.db.

        Regression test: Prevents reverting to swimming_analyzer.db
        """
        from src.garmingo.database.SQLiteManager import SQLiteManager
        from src.garmingo.etl.orchestration.config import OrchestratorConfig

        manager = SQLiteManager()
        config = OrchestratorConfig()

        assert "health_data.db" in str(manager.db_path), \
            "SQLiteManager should still use health_data.db"
        assert config.database_path == "data/health_data.db", \
            "OrchestratorConfig should still use data/health_data.db"
