"""
ETL Jobs module.

This module contains all ETL job implementations organized by source-to-destination flow:
- api_to_cache: Jobs that extract from APIs and load to cache
- cache_to_raw: Jobs that extract from cache and load to raw database tables
- raw_to_processed: Jobs that extract from raw tables and load to processed tables
"""