#!/usr/bin/env python3
"""
Test script for the logging and monitoring system.

This script tests the structured logging, metrics collection, and Discord notifications.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.monitoring.logging_config import StructuredLogger
from src.monitoring.discord_notifier import DiscordNotifier, NotificationConfig
from src.monitoring.metrics_collector import MetricsCollector

def test_structured_logging():
    """Test structured logging functionality."""
    print("🧪 Testing Structured Logging...")
    
    logger = StructuredLogger()
    
    # Test job logging
    job_id = "test_job_001"
    logger.log_job_start(job_id, "recovery", date_range="2024-01-01 to 2024-01-07")
    
    # Simulate some work
    time.sleep(1)
    
    logger.log_job_completion(job_id, 1000.5, 150, job_type="recovery")
    
    # Test API logging
    logger.log_api_request("garmin", "/api/sleep", 200, 250.0, 100, datetime.now())
    
    # Test system metrics
    logger.log_system_metric("cpu_usage", 45.2, {"host": "local"})
    
    print("✅ Structured logging test completed")
    
def test_metrics_collection():
    """Test metrics collection and querying."""
    print("🧪 Testing Metrics Collection...")
    
    collector = MetricsCollector()
    
    # Get job summary
    job_summary = collector.get_job_summary(hours=24)
    print(f"📊 Job Summary: {job_summary}")
    
    # Get API summary
    api_summary = collector.get_api_summary(hours=24)
    print(f"📊 API Summary: {api_summary}")
    
    # Get health status
    health = collector.get_health_status()
    print(f"🏥 Health Status: {health}")
    
    print("✅ Metrics collection test completed")
    
def test_discord_notifications(webhook_url: str = None):
    """Test Discord notifications (requires webhook URL)."""
    print("🧪 Testing Discord Notifications...")
    
    if not webhook_url:
        print("⚠️  No webhook URL provided, skipping Discord test")
        return
        
    config = NotificationConfig(
        webhook_url=webhook_url,
        enabled=True
    )
    
    notifier = DiscordNotifier(config)
    
    # Test webhook connectivity
    if notifier.test_webhook():
        print("✅ Discord webhook test successful")
        
        # Test job notifications
        notifier.send_job_start("test_job_002", "swimming", date_range="2024-01-01")
        time.sleep(1)
        notifier.send_job_success("test_job_002", 2.5, 75, "swimming")
        
        # Test system alert
        notifier.send_system_alert("test_alert", "This is a test system alert", "info")
        
        print("✅ Discord notifications test completed")
    else:
        print("❌ Discord webhook test failed")
        
def test_job_context():
    """Test job context manager."""
    print("🧪 Testing Job Context Manager...")
    
    logger = StructuredLogger()
    
    # Test successful job
    with logger.job_context("test_job_003", "daily_summary", date="2024-01-01"):
        time.sleep(0.5)
        print("  Simulating successful job execution...")
    
    # Test failed job
    try:
        with logger.job_context("test_job_004", "activities", date="2024-01-01"):
            time.sleep(0.5)
            print("  Simulating job failure...")
            raise Exception("Simulated job failure")
    except Exception:
        pass  # Expected failure
        
    print("✅ Job context manager test completed")
    
def main():
    """Run all logging system tests."""
    print("🚀 Starting Logging System Tests")
    print("=" * 50)
    
    # Test structured logging
    test_structured_logging()
    print()
    
    # Test metrics collection
    test_metrics_collection()
    print()
    
    # Test job context manager
    test_job_context()
    print()
    
    # Test Discord notifications (if webhook URL provided)
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    test_discord_notifications(webhook_url)
    print()
    
    print("🎉 All logging system tests completed!")
    print("\n📁 Check the following files:")
    print("  - logs/application.log (structured logs)")
    print("  - logs/errors.log (error logs)")
    print("  - data/metrics.db (metrics database)")
    
    if webhook_url:
        print("  - Discord channel (notifications)")
    else:
        print("\n💡 To test Discord notifications:")
        print("  1. Set up a Discord webhook")
        print("  2. Add DISCORD_WEBHOOK_URL to your .env file")
        print("  3. Run this test again")

if __name__ == "__main__":
    main()
