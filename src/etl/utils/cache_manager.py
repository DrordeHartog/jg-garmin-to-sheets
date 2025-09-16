"""
Cache Manager utility.

Handles cache operations for ETL jobs.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cache operations for ETL jobs."""
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 100):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in MB (default: 100MB)
        """
        self.cache_dir = cache_dir
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CacheManager initialized with cache_dir: {cache_dir}, max_size: {max_size_mb}MB")
    
    def get_cache_file_path(self, target_date: date) -> Path:
        """Get the cache file path for a given date."""
        return self.cache_dir / f"{target_date}.json"
    
    def load_from_cache(self, target_date: date) -> Optional[Dict[str, Any]]:
        """
        Load raw data from cache if it exists.
        
        Args:
            target_date: Date to load cache for
            
        Returns:
            Cached data dictionary if exists, None otherwise
        """
        cache_file = self.get_cache_file_path(target_date)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    raw_data = json.load(f)
                file_size_kb = cache_file.stat().st_size / 1024
                logger.info(f"Loaded cached data for {target_date} ({file_size_kb:.1f} KB)")
                return raw_data
            except Exception as e:
                logger.warning(f"Failed to load cache for {target_date}: {e}")
                return None
        return None
    
    def save_to_cache(self, target_date: date, data: Dict[str, Any]) -> None:
        """
        Save raw data to cache and manage cache size.
        
        Args:
            target_date: Date to save cache for
            data: Data dictionary to cache
        """
        cache_file = self.get_cache_file_path(target_date)
        
        try:
            # Save to cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            file_size_kb = cache_file.stat().st_size / 1024
            logger.info(f"Cached data for {target_date} ({file_size_kb:.1f} KB)")
            
            # Check cache size and cleanup if needed
            self.cleanup_cache_if_needed()
            
        except Exception as e:
            logger.error(f"Failed to save cache for {target_date}: {e}")
    
    def cleanup_cache_if_needed(self) -> None:
        """Clean up cache files if total size exceeds limit."""
        try:
            # Calculate total cache size
            total_size_mb = self.get_cache_size_mb()
            
            if total_size_mb > self.max_size_mb:
                logger.info(f"Cache size ({total_size_mb:.1f} MB) exceeds limit ({self.max_size_mb} MB), cleaning up...")
                
                # Get all cache files sorted by modification time (oldest first)
                cache_files = sorted(
                    self.cache_dir.glob("*.json"),
                    key=lambda f: f.stat().st_mtime
                )
                
                # Remove oldest files until under limit
                for cache_file in cache_files:
                    if total_size_mb <= self.max_size_mb * 0.8:  # Clean to 80% of limit
                        break
                    
                    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
                    cache_file.unlink()
                    total_size_mb -= file_size_mb
                    logger.info(f"Removed old cache file: {cache_file.name}")
                
                logger.info(f"Cache cleanup complete. New size: {total_size_mb:.1f} MB")
                
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    def get_cache_size_mb(self) -> float:
        """
        Get current cache size in MB.
        
        Returns:
            Total cache size in megabytes
        """
        try:
            total_size_bytes = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
            return total_size_bytes / (1024 * 1024)
        except Exception as e:
            logger.error(f"Failed to calculate cache size: {e}")
            return 0.0
    
    def get_cached_files(self, target_date: Optional[date] = None) -> list[Path]:
        """
        Get list of cached files.
        
        Args:
            target_date: If provided, return only the cache file for this date
            
        Returns:
            List of cache file paths
        """
        if target_date:
            cache_file = self.get_cache_file_path(target_date)
            return [cache_file] if cache_file.exists() else []
        else:
            return list(self.cache_dir.glob("*.json"))
    
    def clear_cache(self) -> None:
        """Clear all cache files."""
        try:
            cache_files = self.get_cached_files()
            for cache_file in cache_files:
                cache_file.unlink()
                logger.info(f"Removed cache file: {cache_file.name}")
            logger.info(f"Cache cleared. Removed {len(cache_files)} files.")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
