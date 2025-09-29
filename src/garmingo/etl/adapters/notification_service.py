"""
Notification Service.

Handles Discord webhook notifications for ETL job events.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending Discord notifications."""
    
    def __init__(self, webhook_url: str, enabled: bool = True):
        """
        Initialize notification service.
        
        Args:
            webhook_url: Discord webhook URL
            enabled: Whether notifications are enabled
        """
        self.webhook_url = webhook_url
        self.enabled = enabled
        logger.info(f"NotificationService initialized - enabled: {enabled}")
    
    async def send_job_started(self, job_id: str, job_name: str, target_date: Optional[str] = None) -> bool:
        """
        Send notification when a job starts.
        
        Args:
            job_id: Job identifier
            job_name: Human-readable job name
            target_date: Optional target date for the job
            
        Returns:
            True if notification was sent successfully
        """
        if not self.enabled:
            return True
        
        embed = {
            "title": "🚀 ETL Job Started",
            "description": f"**Job:** {job_name}\n**ID:** {job_id}",
            "color": 0x3498db,  # Blue
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }
        
        if target_date:
            embed["fields"].append({
                "name": "Target Date",
                "value": target_date,
                "inline": True
            })
        
        return await self._send_embed(embed)
    
    async def send_job_completed(self, job_id: str, job_name: str, duration_ms: float, 
                                records_processed: int, target_date: Optional[str] = None) -> bool:
        """
        Send notification when a job completes successfully.
        
        Args:
            job_id: Job identifier
            job_name: Human-readable job name
            duration_ms: Job duration in milliseconds
            records_processed: Number of records processed
            target_date: Optional target date for the job
            
        Returns:
            True if notification was sent successfully
        """
        if not self.enabled:
            return True
        
        duration_seconds = duration_ms / 1000
        embed = {
            "title": "✅ ETL Job Completed",
            "description": f"**Job:** {job_name}\n**ID:** {job_id}",
            "color": 0x2ecc71,  # Green
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Duration",
                    "value": f"{duration_seconds:.1f}s",
                    "inline": True
                },
                {
                    "name": "Records Processed",
                    "value": str(records_processed),
                    "inline": True
                }
            ]
        }
        
        if target_date:
            embed["fields"].append({
                "name": "Target Date",
                "value": target_date,
                "inline": True
            })
        
        return await self._send_embed(embed)
    
    async def send_job_failed(self, job_id: str, job_name: str, error: str, 
                             duration_ms: Optional[float] = None, target_date: Optional[str] = None) -> bool:
        """
        Send notification when a job fails.
        
        Args:
            job_id: Job identifier
            job_name: Human-readable job name
            error: Error message
            duration_ms: Optional job duration in milliseconds
            target_date: Optional target date for the job
            
        Returns:
            True if notification was sent successfully
        """
        if not self.enabled:
            return True
        
        embed = {
            "title": "❌ ETL Job Failed",
            "description": f"**Job:** {job_name}\n**ID:** {job_id}",
            "color": 0xe74c3c,  # Red
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Error",
                    "value": error[:1000],  # Discord field limit
                    "inline": False
                }
            ]
        }
        
        if duration_ms:
            duration_seconds = duration_ms / 1000
            embed["fields"].append({
                "name": "Duration",
                "value": f"{duration_seconds:.1f}s",
                "inline": True
            })
        
        if target_date:
            embed["fields"].append({
                "name": "Target Date",
                "value": target_date,
                "inline": True
            })
        
        return await self._send_embed(embed)
    
    async def send_batch_summary(self, results: list, total_duration_ms: float) -> bool:
        """
        Send notification for batch job execution summary.
        
        Args:
            results: List of JobResult objects
            total_duration_ms: Total duration for all jobs
            
        Returns:
            True if notification was sent successfully
        """
        if not self.enabled:
            return True
        
        successful = sum(1 for r in results if r.status.value == "completed")
        failed = len(results) - successful
        
        embed = {
            "title": "📊 ETL Batch Summary",
            "description": f"Executed {len(results)} jobs",
            "color": 0x9b59b6,  # Purple
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "✅ Successful",
                    "value": str(successful),
                    "inline": True
                },
                {
                    "name": "❌ Failed",
                    "value": str(failed),
                    "inline": True
                },
                {
                    "name": "⏱️ Total Duration",
                    "value": f"{total_duration_ms/1000:.1f}s",
                    "inline": True
                }
            ]
        }
        
        return await self._send_embed(embed)
    
    async def _send_embed(self, embed: Dict[str, Any]) -> bool:
        """
        Send embed to Discord webhook.
        
        Args:
            embed: Discord embed object
            
        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 204:
                        logger.debug("Discord notification sent successfully")
                        return True
                    else:
                        logger.error(f"Discord webhook failed: {response.status} - {await response.text()}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
