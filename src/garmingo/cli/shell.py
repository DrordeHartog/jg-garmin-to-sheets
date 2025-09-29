"""
Interactive ETL Shell for development and testing.

Provides an interactive command-line interface for running ETL jobs,
inspecting data, and managing the pipeline.
"""

import click
import sys
from typing import List, Dict, Any
from datetime import date, datetime
import json

from garmingo.etl.orchestration.orchestrator import ETLOrchestrator
from garmingo.etl.orchestration.config import OrchestratorConfig
from garmingo.etl.adapters.SQLiteClient import SQLiteClient
from garmingo.database.SQLiteManager import SQLiteManager


class ETLShell:
    """Interactive shell for ETL development and testing."""
    
    def __init__(self):
        """Initialize the ETL shell with orchestrator and database client."""
        self.config = OrchestratorConfig()
        self.orchestrator = ETLOrchestrator(self.config)
        db_manager = SQLiteManager(self.config.database_path)
        self.database_client = SQLiteClient(db_manager)
        self.running = True
        
        # Available commands
        self.commands = {
            'run-job': self._run_job,
            'list-jobs': self._list_jobs,
            'check-data': self._check_data,
            'pipeline-status': self._pipeline_status,
            'clear-cache': self._clear_cache,
            'config': self._config_management,
            'help': self._show_help,
            'exit': self._exit,
            'quit': self._exit,
        }
    
    def run(self):
        """Main shell loop."""
        self._print_welcome()
        
        while self.running:
            try:
                command = input("etl> ").strip()
                if not command:
                    continue
                    
                self._execute_command(command)
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to close the shell.")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _execute_command(self, command: str):
        """Parse and execute a command."""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"❌ Unknown command: {cmd}")
            print("Type 'help' for available commands.")
    
    def _run_job(self, args: List[str]):
        """Run a specific ETL job."""
        if not args:
            print("❌ Usage: run-job <job_id>")
            print("Example: run-job cache_to_raw_swimming_laps_2025-09-12")
            return
        
        job_id = args[0]
        print(f"🚀 Running job: {job_id}")
        
        try:
            result = self.orchestrator.trigger_etl_job(job_id)
            if result.get('status') == 'completed':
                print(f"✅ Job completed successfully")
                print(f"   Records processed: {result.get('records_processed', 0)}")
                print(f"   Duration: {result.get('duration_ms', 0):.2f}ms")
            else:
                print(f"❌ Job failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Job execution failed: {str(e)}")
    
    def _list_jobs(self, args: List[str]):
        """List all available ETL jobs."""
        print("📋 Available ETL Jobs:")
        print()
        
        # Get job configurations from database
        try:
            with self.database_client.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT job_id, job_type, is_active FROM etl_job_config ORDER BY job_type, job_id")
                jobs = cursor.fetchall()
                
                if not jobs:
                    print("   No jobs configured.")
                    return
                
                current_type = None
                for job_id, job_type, is_active in jobs:
                    if job_type != current_type:
                        current_type = job_type
                        print(f"   {job_type.upper()}:")
                    
                    status = "✅ Active" if is_active else "❌ Inactive"
                    print(f"     - {job_id} ({status})")
                    
        except Exception as e:
            print(f"❌ Error listing jobs: {str(e)}")
    
    def _check_data(self, args: List[str]):
        """Check data in database tables."""
        if not args:
            print("❌ Usage: check-data <table_name> [--date YYYY-MM-DD] [--limit N]")
            print("Example: check-data raw_swimming_laps --date 2025-09-12 --limit 5")
            return
        
        table_name = args[0]
        date_filter = None
        limit = 10
        
        # Parse arguments
        i = 1
        while i < len(args):
            if args[i] == '--date' and i + 1 < len(args):
                date_filter = args[i + 1]
                i += 2
            elif args[i] == '--limit' and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            else:
                i += 1
        
        print(f"🔍 Checking data in {table_name}")
        if date_filter:
            print(f"   Date filter: {date_filter}")
        print(f"   Limit: {limit} records")
        print()
        
        try:
            with self.database_client.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query
                query = f"SELECT * FROM {table_name}"
                params = []
                
                if date_filter:
                    query += " WHERE date = ?"
                    params.append(date_filter)
                
                query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                if not rows:
                    print("   No data found.")
                    return
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Print data
                print(f"   Found {len(rows)} records:")
                for i, row in enumerate(rows, 1):
                    print(f"   {i}. {dict(zip(columns, row))}")
                    
        except Exception as e:
            print(f"❌ Error checking data: {str(e)}")
    
    def _pipeline_status(self, args: List[str]):
        """Show overall pipeline status."""
        print("📊 Pipeline Status:")
        print()
        
        try:
            # Check database tables
            with self.database_client.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table counts
                tables = [
                    'raw_daily_summary', 'raw_recovery', 'raw_activities',
                    'raw_swimming_sessions', 'raw_swimming_laps',
                    'processed_swimming_sessions', 'processed_swimming_laps'
                ]
                
                print("   Database Tables:")
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"     {table}: {count} records")
                    except:
                        print(f"     {table}: Table not found")
                
                print()
                
                # Get recent job executions
                print("   Recent Job Executions:")
                cursor.execute("""
                    SELECT job_id, status, start_time, records_processed 
                    FROM etl_job_executions 
                    ORDER BY start_time DESC 
                    LIMIT 5
                """)
                executions = cursor.fetchall()
                
                if executions:
                    for job_id, status, start_time, records in executions:
                        status_icon = "✅" if status == "completed" else "❌"
                        print(f"     {status_icon} {job_id}: {records} records ({start_time})")
                else:
                    print("     No recent executions found")
                    
        except Exception as e:
            print(f"❌ Error getting pipeline status: {str(e)}")
    
    def _clear_cache(self, args: List[str]):
        """Clear cache for a specific date."""
        if not args:
            print("❌ Usage: clear-cache <date>")
            print("Example: clear-cache 2025-09-12")
            return
        
        target_date = args[0]
        print(f"🗑️  Clearing cache for {target_date}")
        
        try:
            cache_key = f"garmin_raw_data_{target_date}"
            self.orchestrator.cache_manager.clear_cache(cache_key)
            print(f"✅ Cache cleared for {target_date}")
        except Exception as e:
            print(f"❌ Error clearing cache: {str(e)}")
    
    def _show_help(self, args: List[str]):
        """Show available commands."""
        print("🏊‍♂️ ETL Shell - Available Commands:")
        print()
        print("   Job Management:")
        print("     run-job <job_id>              - Run a specific ETL job")
        print("     list-jobs                     - List all available jobs")
        print()
        print("   Data Inspection:")
        print("     check-data <table> [options]  - Check data in database tables")
        print("       --date YYYY-MM-DD          - Filter by date")
        print("       --limit N                  - Limit number of records")
        print()
        print("   Pipeline Management:")
        print("     pipeline-status               - Show overall pipeline status")
        print("     clear-cache <date>            - Clear cache for a date")
        print()
        print("   Configuration Management:")
        print("     config list-metrics [source]  - List metrics configuration")
        print("     config list-etl-jobs [type]   - List ETL job configuration")
        print("     config add-metric             - Add new metric (interactive)")
        print("     config add-etl-job            - Add new ETL job (interactive)")
        print("     config disable-metric <id>    - Disable a metric")
        print("     config enable-metric <id>     - Enable a metric")
        print()
        print("   General:")
        print("     help                          - Show this help")
        print("     exit, quit                    - Exit the shell")
        print()
        print("   Examples:")
        print("     run-job cache_to_raw_swimming_laps_2025-09-12")
        print("     check-data raw_swimming_laps --date 2025-09-12 --limit 5")
        print("     pipeline-status")
    
    def _config_management(self, args: List[str]):
        """Configuration management commands."""
        if not args:
            print("❌ Usage: config <subcommand>")
            print("Available subcommands:")
            print("  list-metrics [source]     - List metrics configuration")
            print("  list-etl-jobs [type]      - List ETL job configuration")
            print("  add-metric                - Add a new metric (interactive)")
            print("  add-etl-job               - Add a new ETL job (interactive)")
            print("  disable-metric <id>       - Disable a metric")
            print("  enable-metric <id>        - Enable a metric")
            print("  disable-etl-job <job_id>  - Disable an ETL job")
            print("  enable-etl-job <job_id>   - Enable an ETL job")
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "list-metrics":
            self._list_metrics_config(args[1:] if len(args) > 1 else [])
        elif subcommand == "list-etl-jobs":
            self._list_etl_jobs_config(args[1:] if len(args) > 1 else [])
        elif subcommand == "add-metric":
            self._add_metric_interactive()
        elif subcommand == "add-etl-job":
            self._add_etl_job_interactive()
        elif subcommand == "disable-metric":
            if len(args) < 2:
                print("❌ Usage: config disable-metric <metric_id>")
                return
            self._disable_metric(args[1])
        elif subcommand == "enable-metric":
            if len(args) < 2:
                print("❌ Usage: config enable-metric <metric_id>")
                return
            self._enable_metric(args[1])
        elif subcommand == "disable-etl-job":
            if len(args) < 2:
                print("❌ Usage: config disable-etl-job <job_id>")
                return
            self._disable_etl_job(args[1])
        elif subcommand == "enable-etl-job":
            if len(args) < 2:
                print("❌ Usage: config enable-etl-job <job_id>")
                return
            self._enable_etl_job(args[1])
        else:
            print(f"❌ Unknown config subcommand: {subcommand}")
    
    def _list_metrics_config(self, args: List[str]):
        """List metrics configuration."""
        source = args[0] if args else None
        
        try:
            # This would need to be async, but for now just show a placeholder
            print("📊 Metrics Configuration:")
            print("=" * 50)
            if source:
                print(f"Source: {source}")
            else:
                print("All sources")
            print("\nℹ️  Metrics configuration listing requires async implementation")
            print("   Use the populate script for now: python scripts/populate_metrics_config.py")
            
        except Exception as e:
            print(f"❌ Error listing metrics: {str(e)}")
    
    def _list_etl_jobs_config(self, args: List[str]):
        """List ETL jobs configuration."""
        job_type = args[0] if args else None
        
        try:
            print("⚙️ ETL Jobs Configuration:")
            print("=" * 50)
            if job_type:
                print(f"Job Type: {job_type}")
            else:
                print("All job types")
            print("\nℹ️  ETL jobs configuration listing requires async implementation")
            print("   Use the database directly for now")
            
        except Exception as e:
            print(f"❌ Error listing ETL jobs: {str(e)}")
    
    def _add_metric_interactive(self):
        """Interactive metric addition."""
        print("➕ Add New Metric (Interactive Mode)")
        print("=" * 40)
        print("ℹ️  Interactive metric addition requires async implementation")
        print("   Use the populate script for now: python scripts/populate_metrics_config.py")
    
    def _add_etl_job_interactive(self):
        """Interactive ETL job addition."""
        print("➕ Add New ETL Job (Interactive Mode)")
        print("=" * 40)
        print("ℹ️  Interactive ETL job addition requires async implementation")
        print("   Use the database directly for now")
    
    def _disable_metric(self, metric_id: str):
        """Disable a metric."""
        print(f"🔧 Disabling metric {metric_id}...")
        print("ℹ️  Metric disable requires async implementation")
    
    def _enable_metric(self, metric_id: str):
        """Enable a metric."""
        print(f"🔧 Enabling metric {metric_id}...")
        print("ℹ️  Metric enable requires async implementation")
    
    def _disable_etl_job(self, job_id: str):
        """Disable an ETL job."""
        print(f"🔧 Disabling ETL job {job_id}...")
        print("ℹ️  ETL job disable requires async implementation")
    
    def _enable_etl_job(self, job_id: str):
        """Enable an ETL job."""
        print(f"🔧 Enabling ETL job {job_id}...")
        print("ℹ️  ETL job enable requires async implementation")

    def _exit(self, args: List[str]):
        """Exit the shell."""
        print("👋 Goodbye!")
        self.running = False
    
    def _print_welcome(self):
        """Print welcome message."""
        print("🏊‍♂️ ETL Shell - Interactive Development Environment")
        print("=" * 50)
        print("Type 'help' for available commands or 'exit' to quit.")
        print()


@click.command()
def shell():
    """Start the interactive ETL shell."""
    etl_shell = ETLShell()
    etl_shell.run()


if __name__ == '__main__':
    shell()
