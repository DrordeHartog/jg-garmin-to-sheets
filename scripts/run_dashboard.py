#!/usr/bin/env python3
"""
Swimming Analytics Dashboard Launcher

This script launches the swimming analytics dashboard using Streamlit.
Make sure you have activated your virtual environment and have swim data exported.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Check if we're in the right directory
    if not Path("src/dashboard/swim_dashboard.py").exists():
        print("❌ Error: swim_dashboard.py not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment doesn't appear to be activated.")
        print("Please activate your virtual environment first:")
        print("   source venv/bin/activate")
        print()
    
    # Check if required packages are available
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ Required packages found")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("   pip install streamlit pandas plotly")
        sys.exit(1)
    
    # Check for CSV data
    csv_paths = [
        "output/garmingo_USER1.csv",
        "src/output/garmingo_USER1.csv"
    ]
    
    csv_found = False
    for path in csv_paths:
        if os.path.exists(path):
            print(f"✅ Found CSV data: {path}")
            csv_found = True
            break
    
    if not csv_found:
        print("⚠️  Warning: No CSV data found!")
        print("Please export your Garmin data first using:")
        print("   python -m src.main")
        print()
    
    print("🚀 Launching Swimming Analytics Dashboard...")
    print("📊 Dashboard will open in your browser at http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print()
    
    # Launch the dashboard
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/dashboard/swim_dashboard.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
