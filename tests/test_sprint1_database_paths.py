"""
Sprint 1 Database Path Tests

Tests that verify database paths were standardized to 'data/health_data.db'
across all components during Sprint 1.

Before Sprint 1:
- SQLiteManager: data/swimming_analyzer.db
- create_metrics_config: data/swimming_analyzer.db
- CLI commands: ../data/health_data.db (with ../ prefix)

After Sprint 1:
- All standardized to: data/health_data.db (no ../ prefix)

This standardization ensures all components read/write to the same database file
and prevents data fragmentation across multiple database files.
"""

import pytest
from pathlib import Path
from src.garmingo.database.SQLiteManager import SQLiteManager
from src.garmingo.etl.orchestration.config import OrchestratorConfig


class TestDatabasePathStandardization:
    """Tests for Sprint 1 database path standardization."""

    def test_sqlite_manager_default_path(self):
        """Test SQLiteManager uses health_data.db as default.

        Sprint 1 fix: Changed from 'swimming_analyzer.db' to 'health_data.db'
        File: src/garmingo/database/SQLiteManager.py (line 29)
        """
        manager = SQLiteManager()

        assert manager.db_path.name == "health_data.db", \
            "Default database filename should be health_data.db"
        assert "data" in str(manager.db_path), \
            "Database path should include 'data' directory"

    def test_sqlite_manager_custom_path(self):
        """Test SQLiteManager accepts custom paths."""
        custom_path = "data/custom_test.db"
        manager = SQLiteManager(custom_path)

        assert str(manager.db_path) == custom_path, \
            "SQLiteManager should accept custom paths"

    def test_orchestrator_config_database_path(self):
        """Test OrchestratorConfig uses standardized database path.

        Sprint 1 fix: Standardized to 'data/health_data.db'
        File: src/garmingo/etl/orchestration/config.py (line 33)
        """
        config = OrchestratorConfig()

        assert config.database_path == "data/health_data.db", \
            "OrchestratorConfig default should be data/health_data.db"

    def test_cli_commands_database_path(self):
        """Test CLI commands use correct database path without ../ prefix.

        Sprint 1 fix: Changed from '../data/health_data.db' to 'data/health_data.db'
        File: src/garmingo/cli/etl_commands.py (lines 23, 38, 86, 181)
        """
        from src.garmingo.cli.etl_commands import ETLCommands

        # Check the path used in initialize method
        import inspect
        source = inspect.getsource(ETLCommands.initialize)

        # Should use "data/health_data.db" not "../data/health_data.db"
        assert 'database_path="data/health_data.db"' in source, \
            "CLI should use data/health_data.db without ../ prefix"
        assert 'database_path="../data/health_data.db"' not in source, \
            "CLI should not use ../ prefix in database path"

    def test_all_database_paths_standardized(self):
        """Integration test: Verify all components use the same database path.

        This test ensures there's no data fragmentation across multiple database files.
        """
        # SQLiteManager default
        manager = SQLiteManager()
        manager_path = manager.db_path.name

        # OrchestratorConfig default
        config = OrchestratorConfig()
        config_path = Path(config.database_path).name

        # Both should match
        assert manager_path == config_path == "health_data.db", \
            "All components should use the same database filename"


class TestDatabasePathFormat:
    """Tests for database path format consistency."""

    def test_no_relative_paths_in_defaults(self):
        """Test that default paths don't use ../ prefix.

        Sprint 1 fix: Removed ../ prefixes - paths should be relative to project root.
        """
        config = OrchestratorConfig()

        assert not config.database_path.startswith("../"), \
            "Database path should not start with ../"
        assert not config.cache_dir.startswith("../"), \
            "Cache dir should not start with ../"

    def test_paths_use_forward_slashes(self):
        """Test that paths use forward slashes (platform-independent)."""
        config = OrchestratorConfig()

        assert "/" in config.database_path, \
            "Path should use forward slashes"
        assert "\\" not in config.database_path, \
            "Path should not use backslashes"


class TestDatabasePathCreation:
    """Tests for database directory creation."""

    def test_sqlite_manager_creates_directory(self):
        """Test that SQLiteManager creates parent directories if they don't exist.

        SQLiteManager should call mkdir(parents=True, exist_ok=True)
        """
        # This test verifies the behavior, not the actual creation
        # (actual creation would require file system operations)
        import tempfile
        import shutil

        # Create a temporary directory for testing
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create SQLiteManager with path in temp directory
            test_db_path = temp_dir / "data" / "test.db"
            manager = SQLiteManager(str(test_db_path))

            # Parent directory should be created
            assert manager.db_path.parent.exists(), \
                "SQLiteManager should create parent directory"

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestDatabasePathConsistency:
    """Tests to ensure database path consistency across modules."""

    def test_create_metrics_config_table_path(self):
        """Test that create_metrics_config_table uses standardized path.

        Sprint 1 fix: Changed from 'swimming_analyzer.db' to 'health_data.db'
        File: src/garmingo/database/create_metrics_config_table.py (line 27)
        """
        from src.garmingo.database.create_metrics_config_table import create_metrics_config_table
        import inspect

        source = inspect.getsource(create_metrics_config_table)

        # Should use health_data.db
        assert "health_data.db" in source, \
            "create_metrics_config_table should reference health_data.db"

        # Should NOT use swimming_analyzer.db
        assert "swimming_analyzer.db" not in source, \
            "create_metrics_config_table should not reference old swimming_analyzer.db"

    def test_no_hardcoded_old_paths(self):
        """Test that no old database paths remain in key files."""
        from src.garmingo.database.SQLiteManager import SQLiteManager
        from src.garmingo.etl.orchestration.config import OrchestratorConfig
        import inspect

        # Check SQLiteManager source
        manager_source = inspect.getsource(SQLiteManager)
        assert "swimming_analyzer.db" not in manager_source, \
            "SQLiteManager should not reference old swimming_analyzer.db"

        # Check OrchestratorConfig source
        config_source = inspect.getsource(OrchestratorConfig)
        # OrchestratorConfig doesn't hardcode the path, so this is mainly a sanity check
        assert config_source is not None
