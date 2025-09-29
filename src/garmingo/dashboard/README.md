# 🏊‍♂️ Swimming Analytics Dashboard

A comprehensive web-based dashboard for analyzing your swimming performance data from Garmin Connect.

## Features

### 📊 Performance Overview
- **Key Metrics**: Total swims, distance, duration, average pace
- **Performance Indicators**: Best pace, heart rate trends, SWOLF scores
- **Activity Breakdown**: Pool vs open water swim distribution

### 📈 Interactive Visualizations
- **Distance Trends**: Track your swimming distance over time
- **Pace Analysis**: Distribution and correlation with distance
- **Heart Rate Analysis**: Monitor cardiovascular performance
- **SWOLF Analysis**: Swimming efficiency metrics
- **Stroke Analysis**: Stroke rate and efficiency trends

### 📋 Data Management
- **Smart Data Loading**: Automatically detects CSV files
- **Flexible Data Sources**: Works with multiple file locations
- **Real-time Updates**: Refresh data without restarting

## Quick Start

### 1. Prerequisites
- Python 3.8+ with virtual environment activated
- Required packages: `streamlit`, `pandas`, `plotly`
- Garmin data exported to CSV format

### 2. Launch Dashboard
```bash
# From project root directory
python run_dashboard.py
```

Or directly with Streamlit:
```bash
streamlit run src/dashboard/swim_dashboard.py
```

### 3. Access Dashboard
- Open your browser to `http://localhost:8501`
- Select your CSV data file from the sidebar
- Explore your swimming analytics!

## Dashboard Sections

### 🏊‍♂️ Performance Overview
Displays key performance metrics in an easy-to-read card format:
- Total swims and distance
- Average and best paces
- Heart rate statistics
- SWOLF efficiency scores

### 📈 Distance Trend Over Time
Line chart showing your daily swim distances, helping you:
- Track consistency in training
- Identify patterns in your swimming routine
- Monitor progress over time

### ⚡ Pace Analysis
Two complementary charts:
- **Pace Distribution**: Histogram showing your pace range
- **Pace vs Distance**: Scatter plot revealing distance-pace relationships

### ❤️ Heart Rate Analysis
Cardiovascular performance insights:
- **HR Trend**: Average heart rate over time
- **HR vs Distance**: How heart rate correlates with swim distance

### 🏊 SWOLF Analysis
Swimming efficiency metrics:
- **SWOLF Trend**: Efficiency improvement over time
- **SWOLF vs Pace**: Correlation between efficiency and speed

### 🖐️ Stroke Analysis
Technical swimming metrics:
- **Strokes per Length**: Efficiency per pool length
- **Strokes per Minute**: Cadence analysis

### 📊 Activity Summary
Detailed table of all swim activities with:
- Date, distance, duration
- Pace, heart rate, SWOLF scores
- Sortable and filterable data

## Data Requirements

The dashboard expects CSV files with the following swim-related columns:

### Required Columns
- `Date` - Activity date
- `Swim Activity Count` - Number of swim activities
- `Swim Distance (m)` - Distance in meters
- `Swim Duration (min)` - Duration in minutes

### Optional Columns (for enhanced analysis)
- `Swim Average Pace per 100m` - Average pace per 100m
- `Swim Max Pace per 100m` - Best pace achieved
- `Swim Average HR` - Average heart rate
- `Swim Max HR` - Maximum heart rate
- `Average SWOLF` - Swimming efficiency score
- `Swim Average Strokes per Length` - Strokes per pool length
- `Swim Average Strokes per Minute` - Stroke cadence
- `Pool Swim Count` - Number of pool swims
- `Open Water Swim Count` - Number of open water swims

## Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Visualizations**: Plotly interactive charts
- **Data Processing**: Pandas for data manipulation
- **Responsive Design**: Wide layout with sidebar navigation

### File Structure
```
src/dashboard/
├── swim_dashboard.py    # Main dashboard application
├── README.md           # This documentation
└── __init__.py         # Package initialization
```

### Performance Features
- **Lazy Loading**: Data loaded only when needed
- **Error Handling**: Graceful handling of missing data
- **Memory Efficient**: Optimized for large datasets
- **Real-time Updates**: No page refresh required

## Customization

### Adding New Metrics
1. Update the `calculate_swim_metrics()` function
2. Add new visualization functions
3. Integrate into the main dashboard flow

### Styling
- Modify Streamlit theme in `st.set_page_config()`
- Customize Plotly chart colors and layouts
- Adjust column layouts for different screen sizes

### Data Sources
- Add new CSV file paths to the `csv_paths` list
- Implement database connections for real-time data
- Add API integrations for live Garmin data

## Troubleshooting

### Common Issues

**Dashboard won't start:**
- Ensure virtual environment is activated
- Check that all required packages are installed
- Verify you're in the project root directory

**No data displayed:**
- Confirm CSV file contains swim activities
- Check that `Swim Activity Count` > 0 for relevant rows
- Verify date format is compatible

**Missing visualizations:**
- Some charts require specific data columns
- Check the "Optional Columns" section above
- Charts will show warnings for missing data

### Getting Help
- Check the console output for error messages
- Verify your CSV data structure matches requirements
- Ensure your Garmin export includes swim activities

## Future Enhancements

### Planned Features
- **Goal Tracking**: Set and monitor swimming goals
- **Seasonal Analysis**: Compare performance across seasons
- **Training Load**: Calculate and track training stress
- **Social Features**: Share achievements and compare with others
- **Mobile Optimization**: Better mobile device support

### Advanced Analytics
- **Predictive Modeling**: Forecast performance improvements
- **Fatigue Analysis**: Detect overtraining patterns
- **Technique Insights**: Advanced stroke analysis
- **Race Planning**: Optimal pacing strategies

---

*Dashboard powered by Streamlit and Plotly*
