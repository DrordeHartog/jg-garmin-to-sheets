#!/usr/bin/env python3
"""
Script to test and query the recovery table data.

This script will:
1. Connect to the database
2. Run various SQL queries to analyze the data
3. Show data quality and insights
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.database_manager import DatabaseManager
from src.database.schema import create_tables

def test_recovery_data():
    """Test and analyze the recovery table data."""
    
    print("🔍 Testing Recovery Table Data")
    print("=" * 50)
    
    # Connect to database
    db_manager = DatabaseManager("health_data.db")
    
    # Create tables if they don't exist
    with db_manager.get_connection() as conn:
        create_tables(conn)
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Basic table info
        print("\n📊 TABLE OVERVIEW:")
        cursor.execute("SELECT COUNT(*) FROM recovery")
        total_records = cursor.fetchone()[0]
        print(f"Total records: {total_records}")
        
        if total_records == 0:
            print("❌ No data found in recovery table!")
            return
        
        # 2. Date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM recovery")
        min_date, max_date = cursor.fetchone()
        print(f"Date range: {min_date} to {max_date}")
        
        # 3. Data completeness
        print("\n📈 DATA COMPLETENESS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(sleep_score) as sleep_data,
                COUNT(hrv_last_night_avg) as hrv_data,
                COUNT(average_stress) as stress_data,
                COUNT(resting_heart_rate) as hr_data
            FROM recovery
        """)
        completeness = cursor.fetchone()
        print(f"Total records: {completeness[0]}")
        print(f"Sleep data: {completeness[1]} ({completeness[1]/completeness[0]*100:.1f}%)")
        print(f"HRV data: {completeness[2]} ({completeness[2]/completeness[0]*100:.1f}%)")
        print(f"Stress data: {completeness[3]} ({completeness[3]/completeness[0]*100:.1f}%)")
        print(f"Heart rate data: {completeness[4]} ({completeness[4]/completeness[0]*100:.1f}%)")
        
        # 4. Sample data
        print("\n📋 SAMPLE DATA (Latest 10 records):")
        cursor.execute("""
            SELECT date, sleep_score, hrv_status, average_stress, resting_heart_rate
            FROM recovery 
            ORDER BY date DESC 
            LIMIT 10
        """)
        sample_data = cursor.fetchall()
        print(f"{'Date':<12} {'Sleep':<6} {'HRV':<12} {'Stress':<7} {'HR':<4}")
        print("-" * 50)
        for record in sample_data:
            date_str, sleep, hrv, stress, hr = record
            sleep_str = f"{sleep:.1f}" if sleep else "N/A"
            stress_str = f"{stress}" if stress else "N/A"
            hr_str = f"{hr}" if hr else "N/A"
            print(f"{date_str:<12} {sleep_str:<6} {hrv or 'N/A':<12} {stress_str:<7} {hr_str:<4}")
        
        # 5. Sleep score analysis
        print("\n😴 SLEEP SCORE ANALYSIS:")
        cursor.execute("""
            SELECT 
                AVG(sleep_score) as avg_sleep,
                MIN(sleep_score) as min_sleep,
                MAX(sleep_score) as max_sleep,
                COUNT(sleep_score) as sleep_count
            FROM recovery 
            WHERE sleep_score IS NOT NULL
        """)
        sleep_stats = cursor.fetchone()
        if sleep_stats[3] > 0:
            print(f"Average sleep score: {sleep_stats[0]:.1f}")
            print(f"Sleep score range: {sleep_stats[1]:.1f} - {sleep_stats[2]:.1f}")
            print(f"Days with sleep data: {sleep_stats[3]}")
        else:
            print("No sleep score data available")
        
        # 6. HRV status distribution
        print("\n💓 HRV STATUS DISTRIBUTION:")
        cursor.execute("""
            SELECT hrv_status, COUNT(*) as count
            FROM recovery 
            WHERE hrv_status IS NOT NULL
            GROUP BY hrv_status
            ORDER BY count DESC
        """)
        hrv_distribution = cursor.fetchall()
        if hrv_distribution:
            for status, count in hrv_distribution:
                print(f"{status}: {count} days")
        else:
            print("No HRV status data available")
        
        # 7. Stress level analysis
        print("\n😰 STRESS LEVEL ANALYSIS:")
        cursor.execute("""
            SELECT 
                AVG(average_stress) as avg_stress,
                MIN(average_stress) as min_stress,
                MAX(average_stress) as max_stress,
                COUNT(average_stress) as stress_count
            FROM recovery 
            WHERE average_stress IS NOT NULL
        """)
        stress_stats = cursor.fetchone()
        if stress_stats[3] > 0:
            print(f"Average stress: {stress_stats[0]:.1f}")
            print(f"Stress range: {stress_stats[1]} - {stress_stats[2]}")
            print(f"Days with stress data: {stress_stats[3]}")
        else:
            print("No stress data available")
        
        # 8. Recent trends (last 7 days)
        print("\n📈 RECENT TRENDS (Last 7 days):")
        cursor.execute("""
            SELECT date, sleep_score, average_stress, hrv_status
            FROM recovery 
            WHERE date >= date('now', '-7 days')
            ORDER BY date DESC
        """)
        recent_data = cursor.fetchall()
        if recent_data:
            print(f"{'Date':<12} {'Sleep':<6} {'Stress':<7} {'HRV':<12}")
            print("-" * 40)
            for record in recent_data:
                date_str, sleep, stress, hrv = record
                sleep_str = f"{sleep:.1f}" if sleep else "N/A"
                stress_str = f"{stress}" if stress else "N/A"
                print(f"{date_str:<12} {sleep_str:<6} {stress_str:<7} {hrv or 'N/A':<12}")
        else:
            print("No recent data available")
        
        # 9. Data quality check
        print("\n🔍 DATA QUALITY CHECK:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN sleep_score IS NOT NULL THEN 1 ELSE 0 END) as sleep_complete,
                SUM(CASE WHEN hrv_status IS NOT NULL THEN 1 ELSE 0 END) as hrv_complete,
                SUM(CASE WHEN average_stress IS NOT NULL THEN 1 ELSE 0 END) as stress_complete
            FROM recovery
        """)
        quality = cursor.fetchone()
        total = quality[0]
        if total > 0:
            print(f"Data completeness:")
            print(f"  Sleep data: {quality[1]}/{total} ({quality[1]/total*100:.1f}%)")
            print(f"  HRV data: {quality[2]}/{total} ({quality[2]/total*100:.1f}%)")
            print(f"  Stress data: {quality[3]}/{total} ({quality[3]/total*100:.1f}%)")
        
        # 10. Missing dates check
        print("\n📅 MISSING DATES CHECK:")
        cursor.execute("""
            WITH RECURSIVE date_series AS (
                SELECT date('2025-07-24') as date
                UNION ALL
                SELECT date(date, '+1 day')
                FROM date_series
                WHERE date < date('now')
            )
            SELECT ds.date
            FROM date_series ds
            LEFT JOIN recovery r ON ds.date = r.date
            WHERE r.date IS NULL
            ORDER BY ds.date
        """)
        missing_dates = cursor.fetchall()
        if missing_dates:
            print(f"Missing dates: {len(missing_dates)}")
            if len(missing_dates) <= 10:
                for date_tuple in missing_dates:
                    print(f"  {date_tuple[0]}")
            else:
                print(f"  First 5: {', '.join([d[0] for d in missing_dates[:5]])}")
                print(f"  Last 5: {', '.join([d[0] for d in missing_dates[-5:]])}")
        else:
            print("No missing dates - all dates have data!")
    
    print("\n✅ Recovery table analysis completed!")

if __name__ == "__main__":
    test_recovery_data()
