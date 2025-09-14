#!/usr/bin/env python3
"""
ETL CLI entry point.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

# Set PYTHONPATH to avoid relative import issues
os.environ['PYTHONPATH'] = src_path

import asyncio
from cli.etl_commands import main

if __name__ == "__main__":
    asyncio.run(main())
