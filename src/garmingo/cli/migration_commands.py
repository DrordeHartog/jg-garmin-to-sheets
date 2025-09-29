"""
CLI commands for database migration operations.
"""

import click
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.database.migrate_to_raw_schema import run_migration, validate_migration

logger = logging.getLogger(__name__)


@click.group()
def migration():
    """Database migration commands."""
    pass


@migration.command()
@click.option('--db-path', default='data/health_data.db', help='Path to the SQLite database')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def migrate(db_path: str, verbose: bool):
    """Run database migration to separate raw and processed tables."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    click.echo(f"Starting database migration for: {db_path}")
    
    try:
        results = run_migration(db_path)
        
        click.echo("\n✅ Migration completed successfully!")
        click.echo(f"Renamed tables: {len(results['renamed_tables'])}")
        for rename in results['renamed_tables']:
            click.echo(f"  - {rename}")
        
        if results['schema_updates']:
            click.echo(f"Schema updates: {len(results['schema_updates'])}")
            for update in results['schema_updates']:
                click.echo(f"  - {update}")
        
        click.echo(f"Created processed tables: {len(results['created_processed_tables'])}")
        for table in results['created_processed_tables']:
            click.echo(f"  - {table}")
        
        if results['errors']:
            click.echo(f"\n⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                click.echo(f"  - {error}")
    
    except Exception as e:
        click.echo(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)


@migration.command()
@click.option('--db-path', default='data/health_data.db', help='Path to the SQLite database')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def validate(db_path: str, verbose: bool):
    """Validate database migration results."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    click.echo(f"Validating database migration for: {db_path}")
    
    try:
        results = validate_migration(db_path)
        
        click.echo("\n✅ Validation completed!")
        click.echo(f"Raw tables found: {len(results['raw_tables'])}")
        for table in results['raw_tables']:
            click.echo(f"  - {table}")
        
        click.echo(f"Processed tables found: {len(results['processed_tables'])}")
        for table in results['processed_tables']:
            click.echo(f"  - {table}")
        
        if results['schema_validation']:
            click.echo("\nSchema validation:")
            for table, validation in results['schema_validation'].items():
                click.echo(f"  - {table}:")
                for key, value in validation.items():
                    click.echo(f"    - {key}: {value}")
        
        if results['errors']:
            click.echo(f"\n⚠️  Validation errors: {len(results['errors'])}")
            for error in results['errors']:
                click.echo(f"  - {error}")
    
    except Exception as e:
        click.echo(f"\n❌ Validation failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    migration()
