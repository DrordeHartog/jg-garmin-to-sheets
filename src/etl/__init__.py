"""
ETL (Extract, Transform, Load) module for health data processing.

This module provides a clean, job-based ETL architecture where each job
encapsulates a complete E-T-L flow for a specific source-to-destination.

Structure:
- jobs/: ETL job implementations organized by flow type
- services/: External service clients (Garmin API, etc.)
- utils/: Shared utilities for data transformation and validation
- database/: Database operations and migrations
- orchestration/: Job coordination and scheduling
"""
