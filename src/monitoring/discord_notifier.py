"""
Discord webhook notifications for ETL pipeline.

Provides rich Discord notifications for job status, errors, and system health.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class NotificationConfig:
    """Configuration for Discord notifications."""
    webhook_url: str
    enabled: bool = True
    send_job_start: bool = True
    send_job_success: bool = True
    send_job_failure: bool = True
    send_rate_limits: bool = True
    send_system_alerts: bool = True

class DiscordNotifier:
    """Handles Discord webhook notifications for ETL pipeline."""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.session = requests.Session()
        
    def send_job_start(self, job_id: str, job_type: str, **metadata):
        """Send job start notification."""
        if not self.config.enabled or not self.config.send_job_start:
            return
            
        payload = {
            "content": "🚀 **ETL Job Started**",
            "embeds": [{
                "title": f"{job_type.replace('_', ' ').title()} Data Processing",
                "color": 65280,  # Green
                "fields": [
                    {"name": "Job ID", "value": job_id, "inline": True},
                    {"name": "Status", "value": "Running", "inline": True},
                    {"name": "Started", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        # Add metadata fields if provided
        if metadata:
            for key, value in list(metadata.items())[:3]:  # Limit to 3 additional fields
                payload["embeds"][0]["fields"].append({
                    "name": key.replace('_', ' ').title(),
                    "value": str(value),
                    "inline": True
                })
        
        self._send_message(payload)
        
    def send_job_success(self, job_id: str, duration_seconds: float, 
                        records_processed: int, job_type: str, **metadata):
        """Send job success notification."""
        if not self.config.enabled or not self.config.send_job_success:
            return
            
        # Determine color based on duration
        if duration_seconds < 60:
            color = 65280  # Green
        elif duration_seconds < 300:
            color = 16776960  # Yellow
        else:
            color = 16711680  # Red
            
        payload = {
            "content": "✅ **ETL Job Completed Successfully**",
            "embeds": [{
                "title": f"{job_type.replace('_', ' ').title()} Processing Complete",
                "color": color,
                "fields": [
                    {"name": "Job ID", "value": job_id, "inline": True},
                    {"name": "Duration", "value": f"{duration_seconds:.1f}s", "inline": True},
                    {"name": "Records Processed", "value": f"{records_processed:,}", "inline": True},
                    {"name": "Completed", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        self._send_message(payload)
        
    def send_job_failure(self, job_id: str, error: str, job_type: str, **metadata):
        """Send job failure notification."""
        if not self.config.enabled or not self.config.send_job_failure:
            return
            
        payload = {
            "content": "❌ **ETL Job Failed**",
            "embeds": [{
                "title": f"{job_type.replace('_', ' ').title()} Processing Failed",
                "color": 15158332,  # Red
                "fields": [
                    {"name": "Job ID", "value": job_id, "inline": True},
                    {"name": "Error", "value": error[:1000], "inline": False},  # Limit error length
                    {"name": "Failed", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        self._send_message(payload)
        
    def send_rate_limit_alert(self, service: str, retry_after: int, **metadata):
        """Send rate limiting alert."""
        if not self.config.enabled or not self.config.send_rate_limits:
            return
            
        payload = {
            "content": "⚠️ **Rate Limit Exceeded**",
            "embeds": [{
                "title": f"{service} API Rate Limited",
                "color": 16776960,  # Yellow
                "fields": [
                    {"name": "Service", "value": service, "inline": True},
                    {"name": "Retry After", "value": f"{retry_after} seconds", "inline": True},
                    {"name": "Status", "value": "Backing off", "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        self._send_message(payload)
        
    def send_system_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Send system health alert."""
        if not self.config.enabled or not self.config.send_system_alerts:
            return
            
        # Determine color based on severity
        color_map = {
            "info": 3447003,      # Blue
            "warning": 16776960,  # Yellow
            "error": 15158332,    # Red
            "critical": 10038562  # Dark red
        }
        
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        payload = {
            "content": f"{emoji_map.get(severity, '⚠️')} **System Alert**",
            "embeds": [{
                "title": f"{alert_type.replace('_', ' ').title()} Alert",
                "color": color_map.get(severity, 16776960),
                "description": message,
                "fields": [
                    {"name": "Severity", "value": severity.upper(), "inline": True},
                    {"name": "Time", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        self._send_message(payload)
        
    def send_daily_summary(self, summary_data: Dict[str, Any]):
        """Send daily ETL summary."""
        if not self.config.enabled:
            return
            
        total_jobs = summary_data.get('total_jobs', 0)
        successful_jobs = summary_data.get('successful_jobs', 0)
        failed_jobs = summary_data.get('failed_jobs', 0)
        total_records = summary_data.get('total_records', 0)
        
        success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Determine color based on success rate
        if success_rate >= 95:
            color = 65280  # Green
        elif success_rate >= 80:
            color = 16776960  # Yellow
        else:
            color = 15158332  # Red
            
        payload = {
            "content": "📊 **Daily ETL Summary**",
            "embeds": [{
                "title": f"ETL Pipeline Report - {datetime.now().strftime('%Y-%m-%d')}",
                "color": color,
                "fields": [
                    {"name": "Total Jobs", "value": str(total_jobs), "inline": True},
                    {"name": "Successful", "value": str(successful_jobs), "inline": True},
                    {"name": "Failed", "value": str(failed_jobs), "inline": True},
                    {"name": "Success Rate", "value": f"{success_rate:.1f}%", "inline": True},
                    {"name": "Records Processed", "value": f"{total_records:,}", "inline": True},
                    {"name": "Date", "value": datetime.now().strftime("%Y-%m-%d"), "inline": True}
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "ETL Pipeline Monitor"}
            }]
        }
        
        self._send_message(payload)
        
    def _send_message(self, payload: Dict[str, Any]):
        """Send message to Discord webhook."""
        try:
            response = self.session.post(
                self.config.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            # Log error but don't raise - we don't want Discord failures to break ETL
            print(f"Failed to send Discord notification: {e}")
            
    def test_webhook(self) -> bool:
        """Test webhook connectivity."""
        try:
            payload = {
                "content": "🧪 **Webhook Test**",
                "embeds": [{
                    "title": "ETL Pipeline Webhook Test",
                    "description": "This is a test message to verify webhook connectivity.",
                    "color": 3447003,  # Blue
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "ETL Pipeline Monitor"}
                }]
            }
            
            response = self.session.post(
                self.config.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Webhook test failed: {e}")
            return False
