"""
Logging configuration for the Garmin data fetching system.
"""
import logging
import os
from pathlib import Path
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogOutput = Literal["console", "file", "both", "none"]

class LoggingConfig:
    """Configurable logging system."""
    
    def __init__(self, 
                 level: LogLevel = "INFO",
                 output: LogOutput = "console",
                 log_file: str = "logs/garmin_data.log"):
        self.level = level
        self.output = output
        self.log_file = log_file
        
    def setup_logging(self):
        """Setup logging based on configuration."""
        # Create logs directory if it doesn't exist
        if self.output in ["file", "both"]:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.level))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler
        if self.output in ["console", "both"]:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.level))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Add file handler
        if self.output in ["file", "both"]:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(getattr(logging, self.level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Set specific logger levels
        logging.getLogger('src.core.garmin_client').setLevel(getattr(logging, self.level))
        
        return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

# Default configuration
DEFAULT_CONFIG = LoggingConfig(
    level="INFO",
    output="console",
    log_file="logs/garmin_data.log"
)

# Global logger instance
_logger = None

def setup_default_logging():
    """Setup default logging configuration."""
    global _logger
    _logger = DEFAULT_CONFIG.setup_logging()
    return _logger

def setup_custom_logging(level: LogLevel = "INFO", 
                        output: LogOutput = "console",
                        log_file: str = "logs/garmin_data.log"):
    """Setup custom logging configuration."""
    global _logger
    config = LoggingConfig(level=level, output=output, log_file=log_file)
    _logger = config.setup_logging()
    return _logger

def log_swimming_data(logger, data, data_type="Unknown"):
    """
    Log swimming data with detailed analysis.
    
    Args:
        logger: Logger instance
        data: Data to analyze for swimming content
        data_type: Type of data being logged (e.g., "activities", "summary", "stats")
    """
    import json
    
    logger.info(f"=== SWIMMING DATA ANALYSIS for {data_type} ===")
    
    if not data:
        logger.info(f"No {data_type} data available")
        return
    
    try:
        # Convert to JSON for analysis
        json_str = json.dumps(data, indent=2, default=str)
        
        # Look for swimming-related content
        swimming_indicators = [
            'lap_swimming', 'swim', 'pool', 'strokes', 'swolf', 
            'swimCadence', 'activeLengths', 'poolLength'
        ]
        
        found_swimming = False
        for indicator in swimming_indicators:
            if indicator.lower() in json_str.lower():
                logger.info(f"✅ Found swimming indicator: '{indicator}'")
                found_swimming = True
        
        if not found_swimming:
            logger.info(f"❌ No swimming indicators found in {data_type}")
            return
        
        # If it's a list (like activities), analyze each item
        if isinstance(data, list):
            logger.info(f"Analyzing {len(data)} items in {data_type}")
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    activity_type = item.get('activityType', {})
                    type_key = activity_type.get('typeKey', '')
                    activity_name = item.get('activityName', 'Unknown')
                    
                    if 'swim' in type_key.lower():
                        logger.info(f"🏊‍♂️ SWIMMING ACTIVITY #{i+1}: {activity_name}")
                        logger.info(f"   Type: {type_key} (ID: {activity_type.get('typeId')})")
                        logger.info(f"   Distance: {item.get('distance', 'N/A')} meters")
                        logger.info(f"   Duration: {item.get('duration', 'N/A')} seconds")
                        logger.info(f"   Strokes: {item.get('strokes', 'N/A')}")
                        logger.info(f"   SWOLF: {item.get('averageSwolf', 'N/A')}")
                        logger.info(f"   Laps: {item.get('lapCount', 'N/A')}")
                        logger.info(f"   Active Lengths: {item.get('activeLengths', 'N/A')}")
                        logger.info(f"   Pool Length: {item.get('poolLength', 'N/A')} meters")
                        logger.info(f"   Avg HR: {item.get('averageHR', 'N/A')}")
                        logger.info(f"   Max HR: {item.get('maxHR', 'N/A')}")
                        logger.info(f"   Swim Cadence: {item.get('averageSwimCadenceInStrokesPerMinute', 'N/A')} strokes/min")
                        logger.info(f"   Full activity data: {json.dumps(item, indent=4, default=str)}")
        
        # If it's a dict, look for swimming-related keys
        elif isinstance(data, dict):
            logger.info(f"Analyzing dictionary with {len(data)} keys")
            
            # Look for bodyBatteryActivityEventList (where swimming might be)
            if 'bodyBatteryActivityEventList' in data:
                events = data['bodyBatteryActivityEventList']
                logger.info(f"Found bodyBatteryActivityEventList with {len(events)} events")
                for i, event in enumerate(events):
                    if isinstance(event, dict):
                        event_type = event.get('eventType', '')
                        if isinstance(event_type, str):
                            if 'swim' in event_type.lower():
                                logger.info(f"🏊‍♂️ SWIMMING EVENT #{i+1}: {event_type}")
                                logger.info(f"   Full event data: {json.dumps(event, indent=4, default=str)}")
                        elif isinstance(event_type, dict):
                            event_key = event_type.get('typeKey', '')
                            if 'swim' in event_key.lower():
                                logger.info(f"🏊‍♂️ SWIMMING EVENT #{i+1}: {event_key}")
                                logger.info(f"   Full event data: {json.dumps(event, indent=4, default=str)}")
                        else:
                            logger.debug(f"Event {i+1} eventType is neither string nor dict: {type(event_type)}")
                    else:
                        logger.debug(f"Event {i+1} is not a dict: {type(event)}")
            
            # Look for other swimming-related keys
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in swimming_indicators):
                    logger.info(f"🏊‍♂️ Swimming-related key '{key}': {value}")
        
        logger.info(f"=== END SWIMMING DATA ANALYSIS for {data_type} ===")
        
    except Exception as e:
        logger.error(f"Error analyzing swimming data: {e}")
        logger.debug(f"Raw data: {str(data)[:1000]}...")
