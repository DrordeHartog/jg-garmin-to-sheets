import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent))

def load_swim_data(csv_path: str = "output/garmingo_USER1.csv") -> pd.DataFrame:
    """Load and preprocess swim data from CSV."""
    try:
        df = pd.read_csv(csv_path)
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter for swim-related columns and date
        swim_columns = [
            'Date', 'Swim Activity Count', 'Swim Distance (m)', 'Swim Laps',
            'Swim Duration (min)', 'Pool Swim Count', 'Open Water Swim Count',
            'Swim Average Pace per 100m', 'Swim Max Pace per 100m',
            'Swim Average HR', 'Swim Max HR', 'Swim Average Strokes per Length',
            'Swim Average Strokes per Minute', 'Average SWOLF', 'Total Strokes'
        ]
        
        # Only keep columns that exist in the dataframe
        existing_columns = [col for col in swim_columns if col in df.columns]
        swim_df = df[existing_columns].copy()
        
        # Convert numeric columns, handling empty strings
        numeric_columns = [col for col in existing_columns if col != 'Date']
        for col in numeric_columns:
            swim_df[col] = pd.to_numeric(swim_df[col], errors='coerce')
        
        # Filter out rows with no swim activity
        swim_df = swim_df[swim_df['Swim Activity Count'] > 0].copy()
        
        return swim_df
        
    except FileNotFoundError:
        st.error(f"CSV file not found: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def format_pace_mmss(seconds_per_100m):
    """Convert seconds per 100m to mm:ss format."""
    if pd.isna(seconds_per_100m) or seconds_per_100m <= 0:
        return "N/A"
    
    minutes = int(seconds_per_100m // 60)
    seconds = int(seconds_per_100m % 60)
    return f"{minutes:02d}:{seconds:02d}"

def calculate_swim_metrics(df: pd.DataFrame) -> dict:
    """Calculate key swimming performance metrics."""
    if df.empty:
        return {}
    
    # Calculate raw pace values
    avg_pace_raw = float(df['Swim Average Pace per 100m'].mean()) if 'Swim Average Pace per 100m' in df.columns else None
    best_pace_raw = float(df['Swim Max Pace per 100m'].min()) if 'Swim Max Pace per 100m' in df.columns else None
    
    metrics = {
        'total_swims': int(df['Swim Activity Count'].sum()),
        'total_distance': float(df['Swim Distance (m)'].sum()),
        'total_duration': float(df['Swim Duration (min)'].sum()),
        'avg_pace_raw': avg_pace_raw,
        'avg_pace_formatted': format_pace_mmss(avg_pace_raw),
        'best_pace_raw': best_pace_raw,
        'best_pace_formatted': format_pace_mmss(best_pace_raw),
        'avg_hr': float(df['Swim Average HR'].mean()) if 'Swim Average HR' in df.columns else None,
        'max_hr': float(df['Swim Max HR'].max()) if 'Swim Max HR' in df.columns else None,
        'avg_swolf': float(df['Average SWOLF'].mean()) if 'Average SWOLF' in df.columns else None,
        'pool_swims': int(df['Pool Swim Count'].sum()) if 'Pool Swim Count' in df.columns else 0,
        'open_water_swims': int(df['Open Water Swim Count'].sum()) if 'Open Water Swim Count' in df.columns else 0,
    }
    
    return metrics

def create_performance_overview(df: pd.DataFrame):
    """Create performance overview section with key metrics."""
    st.header("🏊‍♂️ Swimming Performance Overview")
    
    metrics = calculate_swim_metrics(df)
    
    if not metrics:
        st.warning("No swim data available. Please ensure your CSV file contains swim activities.")
        return
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Swims",
            value=metrics['total_swims'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Distance",
            value=f"{metrics['total_distance']:,.0f}m",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Duration",
            value=f"{metrics['total_duration']:.0f}min",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Avg Pace",
            value=metrics['avg_pace_formatted'],
            delta=None
        )
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="Best Pace",
            value=metrics['best_pace_formatted'],
            delta=None
        )
    
    with col6:
        avg_hr_str = f"{metrics['avg_hr']:.0f} bpm" if metrics['avg_hr'] else "N/A"
        st.metric(
            label="Avg Heart Rate",
            value=avg_hr_str,
            delta=None
        )
    
    with col7:
        avg_swolf_str = f"{metrics['avg_swolf']:.0f}" if metrics['avg_swolf'] else "N/A"
        st.metric(
            label="Avg SWOLF",
            value=avg_swolf_str,
            delta=None
        )
    
    with col8:
        pool_ratio = f"{metrics['pool_swims']}/{metrics['open_water_swims']}"
        st.metric(
            label="Pool/Open Water",
            value=pool_ratio,
            delta=None
        )

def create_distance_trend_chart(df: pd.DataFrame):
    """Create distance trend over time chart."""
    st.subheader("📈 Distance Trend Over Time")
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    # Group by date and sum distances
    daily_distance = df.groupby('Date')['Swim Distance (m)'].sum().reset_index()
    
    fig = px.line(
        daily_distance,
        x='Date',
        y='Swim Distance (m)',
        title="Daily Swim Distance",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Distance (meters)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_pace_analysis(df: pd.DataFrame):
    """Create pace analysis charts."""
    st.subheader("⚡ Pace Analysis")
    
    if df.empty or 'Swim Average Pace per 100m' not in df.columns:
        st.warning("Pace data not available")
        return
    
    # Filter out rows with no pace data
    pace_df = df[df['Swim Average Pace per 100m'].notna()].copy()
    
    if pace_df.empty:
        st.warning("No pace data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pace distribution histogram
        fig_hist = px.histogram(
            pace_df,
            x='Swim Average Pace per 100m',
            nbins=20,
            title="Pace Distribution",
            labels={'Swim Average Pace per 100m': 'Pace (seconds/100m)'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Pace vs Distance scatter
        fig_scatter = px.scatter(
            pace_df,
            x='Swim Distance (m)',
            y='Swim Average Pace per 100m',
            title="Pace vs Distance",
            labels={
                'Swim Distance (m)': 'Distance (meters)',
                'Swim Average Pace per 100m': 'Pace (seconds/100m)'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def create_heart_rate_analysis(df: pd.DataFrame):
    """Create heart rate analysis charts."""
    st.subheader("❤️ Heart Rate Analysis")
    
    if df.empty or 'Swim Average HR' not in df.columns:
        st.warning("Heart rate data not available")
        return
    
    # Filter out rows with no HR data
    hr_df = df[df['Swim Average HR'].notna()].copy()
    
    if hr_df.empty:
        st.warning("No heart rate data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # HR trend over time
        fig_hr_trend = px.line(
            hr_df,
            x='Date',
            y='Swim Average HR',
            title="Average Heart Rate Trend",
            markers=True
        )
        fig_hr_trend.update_layout(yaxis_title="Heart Rate (bpm)")
        st.plotly_chart(fig_hr_trend, use_container_width=True)
    
    with col2:
        # HR vs Distance
        fig_hr_distance = px.scatter(
            hr_df,
            x='Swim Distance (m)',
            y='Swim Average HR',
            title="Heart Rate vs Distance",
            labels={
                'Swim Distance (m)': 'Distance (meters)',
                'Swim Average HR': 'Heart Rate (bpm)'
            }
        )
        st.plotly_chart(fig_hr_distance, use_container_width=True)

def create_swolf_analysis(df: pd.DataFrame):
    """Create SWOLF analysis charts."""
    st.subheader("🏊 SWOLF Analysis")
    
    if df.empty or 'Average SWOLF' not in df.columns:
        st.warning("SWOLF data not available")
        return
    
    # Filter out rows with no SWOLF data
    swolf_df = df[df['Average SWOLF'].notna()].copy()
    
    if swolf_df.empty:
        st.warning("No SWOLF data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SWOLF trend over time
        fig_swolf_trend = px.line(
            swolf_df,
            x='Date',
            y='Average SWOLF',
            title="SWOLF Trend Over Time",
            markers=True
        )
        fig_swolf_trend.update_layout(yaxis_title="SWOLF Score")
        st.plotly_chart(fig_swolf_trend, use_container_width=True)
    
    with col2:
        # SWOLF vs Pace correlation
        if 'Swim Average Pace per 100m' in swolf_df.columns:
            pace_swolf_df = swolf_df[swolf_df['Swim Average Pace per 100m'].notna()]
            if not pace_swolf_df.empty:
                fig_swolf_pace = px.scatter(
                    pace_swolf_df,
                    x='Swim Average Pace per 100m',
                    y='Average SWOLF',
                    title="SWOLF vs Pace",
                    labels={
                        'Swim Average Pace per 100m': 'Pace (seconds/100m)',
                        'Average SWOLF': 'SWOLF Score'
                    }
                )
                st.plotly_chart(fig_swolf_pace, use_container_width=True)
            else:
                st.info("No pace data available for SWOLF correlation")
        else:
            st.info("Pace data not available for SWOLF correlation")

def create_stroke_analysis(df: pd.DataFrame):
    """Create stroke analysis charts."""
    st.subheader("🖐️ Stroke Analysis")
    
    stroke_columns = ['Swim Average Strokes per Length', 'Swim Average Strokes per Minute']
    available_stroke_cols = [col for col in stroke_columns if col in df.columns]
    
    if not available_stroke_cols:
        st.warning("Stroke data not available")
        return
    
    # Filter out rows with no stroke data
    stroke_df = df[df[available_stroke_cols].notna().any(axis=1)].copy()
    
    if stroke_df.empty:
        st.warning("No stroke data available")
        return
    
    if len(available_stroke_cols) == 2:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_strokes_length = px.line(
                stroke_df,
                x='Date',
                y='Swim Average Strokes per Length',
                title="Strokes per Length Trend",
                markers=True
            )
            st.plotly_chart(fig_strokes_length, use_container_width=True)
        
        with col2:
            fig_strokes_minute = px.line(
                stroke_df,
                x='Date',
                y='Swim Average Strokes per Minute',
                title="Strokes per Minute Trend",
                markers=True
            )
            st.plotly_chart(fig_strokes_minute, use_container_width=True)
    else:
        # If only one stroke metric is available
        fig_stroke = px.line(
            stroke_df,
            x='Date',
            y=available_stroke_cols[0],
            title=f"{available_stroke_cols[0]} Trend",
            markers=True
        )
        st.plotly_chart(fig_stroke, use_container_width=True)

def create_activity_summary(df: pd.DataFrame):
    """Create activity summary table."""
    st.subheader("📊 Activity Summary")
    
    if df.empty:
        st.warning("No data available for summary")
        return
    
    # Create summary table
    summary_data = []
    
    for _, row in df.iterrows():
        if row['Swim Activity Count'] > 0:
            summary_data.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Distance (m)': f"{row['Swim Distance (m)']:.0f}",
                'Duration (min)': f"{row['Swim Duration (min)']:.0f}",
                'Pace (mm:ss/100m)': format_pace_mmss(row['Swim Average Pace per 100m']),
                'HR (bpm)': f"{row['Swim Average HR']:.0f}" if pd.notna(row['Swim Average HR']) else "N/A",
                'SWOLF': f"{row['Average SWOLF']:.0f}" if pd.notna(row['Average SWOLF']) else "N/A"
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("No swim activities found in the data")

def main():
    st.set_page_config(
        page_title="Swimming Analytics Dashboard",
        page_icon="🏊‍♂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏊‍♂️ Swimming Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar for data selection
    st.sidebar.header("📁 Data Source")
    
    # Look for CSV files in common locations
    csv_paths = [
        "output/garmingo_USER1.csv",
        "src/output/garmingo_USER1.csv",
        "../output/garmingo_USER1.csv"
    ]
    
    available_files = []
    for path in csv_paths:
        if os.path.exists(path):
            available_files.append(path)
    
    if available_files:
        selected_file = st.sidebar.selectbox(
            "Select CSV file:",
            available_files,
            index=0
        )
    else:
        st.sidebar.error("No CSV files found. Please run the data export first.")
        st.stop()
    
    # Load data
    with st.spinner("Loading swim data..."):
        df = load_swim_data(selected_file)
    
    if df.empty:
        st.error("No swim data found in the selected file.")
        st.info("Please ensure your CSV file contains swim activities with the following columns:")
        st.code("""
        - Swim Activity Count
        - Swim Distance (m)
        - Swim Duration (min)
        - Swim Average Pace per 100m
        - Swim Average HR
        - Average SWOLF
        """)
        return
    
    # Display data info
    st.sidebar.success(f"✅ Loaded {len(df)} swim activities")
    st.sidebar.info(f"Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    # Main dashboard sections
    create_performance_overview(df)
    st.markdown("---")
    
    create_distance_trend_chart(df)
    st.markdown("---")
    
    create_pace_analysis(df)
    st.markdown("---")
    
    create_heart_rate_analysis(df)
    st.markdown("---")
    
    create_swolf_analysis(df)
    st.markdown("---")
    
    create_stroke_analysis(df)
    st.markdown("---")
    
    create_activity_summary(df)
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard powered by Streamlit and Plotly*")

if __name__ == "__main__":
    main()
