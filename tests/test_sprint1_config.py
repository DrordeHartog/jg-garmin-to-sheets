"""
Sprint 1 Configuration Tests

Tests for configuration classes added or fixed during Sprint 1.

Key addition: NotificationConfig dataclass
- Added to fix missing class reference in OrchestratorConfig (line 30)
- Provides Discord webhook notification settings
- Includes batch notification threshold and event toggles

This test file validates:
1. NotificationConfig can be instantiated with defaults
2. NotificationConfig accepts custom values
3. OrchestratorConfig integrates with NotificationConfig
4. JobStatus enum values are correct
5. JobResult dataclass works properly
"""

import pytest
from datetime import datetime
from src.garmingo.etl.orchestration.config import (
    NotificationConfig,
    OrchestratorConfig,
    JobStatus,
    JobResult,
    JobConfig,
    RateLimit
)


class TestNotificationConfig:
    """Tests for the NotificationConfig dataclass added in Sprint 1."""

    def test_notification_config_creation(self):
        """Test that NotificationConfig can be instantiated with defaults."""
        nc = NotificationConfig()

        assert nc is not None, "NotificationConfig should instantiate"

    def test_notification_config_defaults(self):
        """Test NotificationConfig default values match specification.

        Defaults from Sprint 1:
        - enabled: False (notifications off by default)
        - webhook_url: None (no webhook configured)
        - batch_notification_threshold: 2 (minimum jobs for batch notification)
        - notify_on_success: True
        - notify_on_failure: True
        - notify_on_start: False
        """
        nc = NotificationConfig()

        assert nc.enabled == False, "Notifications should be disabled by default"
        assert nc.webhook_url is None, "No webhook URL by default"
        assert nc.batch_notification_threshold == 2, "Batch threshold should be 2"
        assert nc.notify_on_success == True, "Should notify on success by default"
        assert nc.notify_on_failure == True, "Should notify on failure by default"
        assert nc.notify_on_start == False, "Should not notify on start by default"

    def test_notification_config_custom_values(self):
        """Test NotificationConfig with custom values."""
        nc = NotificationConfig(
            enabled=True,
            webhook_url="https://discord.com/api/webhooks/test",
            batch_notification_threshold=5,
            notify_on_success=False,
            notify_on_failure=True,
            notify_on_start=True
        )

        assert nc.enabled == True, "Should accept custom enabled value"
        assert nc.webhook_url == "https://discord.com/api/webhooks/test", "Should accept custom webhook URL"
        assert nc.batch_notification_threshold == 5, "Should accept custom threshold"
        assert nc.notify_on_success == False, "Should accept custom notify_on_success"
        assert nc.notify_on_failure == True, "Should accept custom notify_on_failure"
        assert nc.notify_on_start == True, "Should accept custom notify_on_start"

    def test_notification_config_partial_override(self):
        """Test that NotificationConfig allows partial overrides."""
        nc = NotificationConfig(
            enabled=True,
            webhook_url="https://example.com/webhook"
            # Other fields should use defaults
        )

        assert nc.enabled == True, "Overridden field should have custom value"
        assert nc.webhook_url == "https://example.com/webhook", "Overridden field should have custom value"
        assert nc.batch_notification_threshold == 2, "Non-overridden field should use default"
        assert nc.notify_on_success == True, "Non-overridden field should use default"


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig with NotificationConfig integration."""

    def test_orchestrator_config_with_notification_config(self):
        """Test OrchestratorConfig can be created with NotificationConfig.

        Sprint 1 fix: OrchestratorConfig line 30 referenced NotificationConfig
        which didn't exist, causing ImportError.
        """
        config = OrchestratorConfig(
            database_path="data/test.db",
            cache_dir="data/test_cache",
            notifications=NotificationConfig(
                enabled=True,
                webhook_url="https://example.com/webhook"
            )
        )

        assert config is not None, "OrchestratorConfig should instantiate"
        assert config.notifications is not None, "Notifications should be set"
        assert config.notifications.enabled == True, "Notification enabled should propagate"
        assert config.notifications.webhook_url == "https://example.com/webhook", "Webhook URL should propagate"

    def test_orchestrator_config_defaults(self):
        """Test OrchestratorConfig default values (database path standardized in Sprint 1).

        Sprint 1 standardization:
        - database_path: "data/health_data.db" (changed from "data/swimming_analyzer.db")
        """
        config = OrchestratorConfig()

        assert config.database_path == "data/health_data.db", "Default DB path should be health_data.db"
        assert config.cache_dir == "data/cache", "Default cache dir should be data/cache"
        assert config.max_concurrent_jobs == 3, "Default concurrent jobs should be 3"
        assert config.notifications is None, "Notifications should be None by default"

    def test_orchestrator_config_with_none_notification(self):
        """Test OrchestratorConfig works with notifications=None."""
        config = OrchestratorConfig(
            database_path="data/test.db",
            notifications=None
        )

        assert config.notifications is None, "Should accept None for notifications"


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_job_status_enum_values(self):
        """Test that JobStatus enum has expected values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"

    def test_job_status_comparison(self):
        """Test JobStatus enum comparisons."""
        assert JobStatus.COMPLETED == JobStatus.COMPLETED
        assert JobStatus.COMPLETED != JobStatus.FAILED


class TestJobResult:
    """Tests for JobResult dataclass."""

    def test_job_result_creation(self):
        """Test JobResult dataclass can be instantiated."""
        result = JobResult(
            job_id="test_job_1",
            status=JobStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_ms=1500.0,
            records_processed=100,
            errors=[]
        )

        assert result is not None, "JobResult should instantiate"
        assert result.job_id == "test_job_1"
        assert result.status == JobStatus.COMPLETED
        assert result.records_processed == 100
        assert result.errors == []

    def test_job_result_with_errors(self):
        """Test JobResult with error list."""
        result = JobResult(
            job_id="test_job_2",
            status=JobStatus.FAILED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_ms=500.0,
            records_processed=0,
            errors=["Connection timeout", "Database locked"]
        )

        assert result.status == JobStatus.FAILED
        assert len(result.errors) == 2
        assert "Connection timeout" in result.errors

    def test_job_result_metadata(self):
        """Test JobResult metadata field."""
        result = JobResult(
            job_id="test_job_3",
            status=JobStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_ms=2000.0,
            records_processed=50,
            errors=[],
            metadata={"source": "cache", "target": "raw_db"}
        )

        assert result.metadata is not None
        assert result.metadata["source"] == "cache"
        assert result.metadata["target"] == "raw_db"


class TestJobConfig:
    """Tests for JobConfig dataclass."""

    def test_job_config_creation(self):
        """Test JobConfig can be instantiated."""
        config = JobConfig(
            job_type="recovery_job",
            priority=1,
            retry_count=3,
            timeout=1800
        )

        assert config is not None
        assert config.job_type == "recovery_job"
        assert config.priority == 1
        assert config.retry_count == 3
        assert config.timeout == 1800


class TestRateLimit:
    """Tests for RateLimit dataclass."""

    def test_rate_limit_creation(self):
        """Test RateLimit can be instantiated."""
        rate_limit = RateLimit(
            requests_per_minute=60,
            requests_per_hour=1000,
            backoff_multiplier=2.0,
            max_backoff_seconds=300
        )

        assert rate_limit is not None
        assert rate_limit.requests_per_minute == 60
        assert rate_limit.requests_per_hour == 1000
        assert rate_limit.backoff_multiplier == 2.0
        assert rate_limit.max_backoff_seconds == 300
