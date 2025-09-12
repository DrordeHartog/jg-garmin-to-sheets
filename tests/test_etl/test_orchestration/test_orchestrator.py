"""
Tests for ETL orchestrator.
"""

import pytest
from src.etl.orchestration import ETLOrchestrator, OrchestratorConfig

class TestETLOrchestrator:
    """Test the main ETL orchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        from src.etl.orchestration.config import NotificationConfig
        notifications = NotificationConfig(discord_webhook_url="https://discord.com/api/webhooks/test")
        config = OrchestratorConfig(notifications=notifications)
        orchestrator = ETLOrchestrator(config)
        assert orchestrator is not None
        
    def test_orchestrator_start_stop(self):
        """Test orchestrator start and stop."""
        from src.etl.orchestration.config import NotificationConfig
        notifications = NotificationConfig(discord_webhook_url="https://discord.com/api/webhooks/test")
        config = OrchestratorConfig(notifications=notifications)
        orchestrator = ETLOrchestrator(config)
        # TODO: Test start/stop functionality
        assert True
