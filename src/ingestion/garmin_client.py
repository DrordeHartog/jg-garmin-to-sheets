from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional, List
import asyncio
import logging
import garminconnect
import json
from garth.sso import resume_login
import garth
from exceptions import MFARequiredException

logger = logging.getLogger(__name__)

@dataclass
class GarminMetrics:
    date: date
    sleep_score: Optional[float] = None
    
    sleep_length: Optional[float] = None
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    active_calories: Optional[int] = None
    resting_calories: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    average_stress: Optional[int] = None
    training_status: Optional[str] = None
    vo2max_running: Optional[float] = None
    intensity_minutes: Optional[int] = None
    all_activity_count: Optional[int] = None
    running_activity_count: Optional[int] = None
    running_distance: Optional[float] = None
    strength_activity_count: Optional[int] = None
    strength_duration: Optional[float] = None
    cardio_activity_count: Optional[int] = None
    cardio_duration: Optional[float] = None
    overnight_hrv: Optional[int] = None
    hrv_status: Optional[str] = None
    # Swimming Activity Counts
    swim_activity_count: Optional[int] = None
    pool_swim_count: Optional[int] = None
    open_water_swim_count: Optional[int] = None
    
    # Swimming Distance & Duration
    swim_distance_meters: Optional[float] = None
    swim_duration_min: Optional[float] = None
    swim_duration_seconds: Optional[float] = None
    
    # Swimming Laps & Lengths
    swim_laps: Optional[int] = None  # Total laps completed
    active_lengths: Optional[int] = None  # Active swimming lengths
    pool_length_meters: Optional[float] = None  # Pool length in meters
    
    # Swimming Pace & Speed
    swim_average_pace_per_100m: Optional[float] = None  # Average pace per 100m in seconds
    swim_max_pace_per_100m: Optional[float] = None  # Max pace per 100m in seconds
    swim_average_speed: Optional[float] = None  # Average speed in m/s
    swim_max_speed: Optional[float] = None  # Max speed in m/s
    
    # Swimming Heart Rate
    swim_average_hr: Optional[float] = None  # Average heart rate during swim
    swim_max_hr: Optional[float] = None  # Max heart rate during swim
    
    # Swimming Strokes & Technique
    total_strokes: Optional[int] = None  # Total strokes taken
    swim_average_strokes_per_length: Optional[float] = None  # Average strokes per length
    swim_average_strokes_per_minute: Optional[float] = None  # Stroke rate (SPM)
    swim_cadence: Optional[float] = None  # Swimming cadence
    
    # Swimming Efficiency Metrics
    avg_swolf: Optional[float] = None  # Average SWOLF score (strokes + time per 50m)
    min_swolf: Optional[float] = None  # Best (minimum) SWOLF score
    max_swolf: Optional[float] = None  # Worst (maximum) SWOLF score
    
    # Swimming Zones & Intensity
    swim_zone1_time: Optional[float] = None  # Time in zone 1 (recovery)
    swim_zone2_time: Optional[float] = None  # Time in zone 2 (aerobic base)
    swim_zone3_time: Optional[float] = None  # Time in zone 3 (tempo)
    swim_zone4_time: Optional[float] = None  # Time in zone 4 (threshold)
    swim_zone5_time: Optional[float] = None  # Time in zone 5 (VO2 max)
    
    # Swimming Calories & Power
    swim_calories: Optional[int] = None  # Calories burned during swim
    swim_training_effect: Optional[float] = None  # Training effect score
    swim_anaerobic_training_effect: Optional[float] = None  # Anaerobic training effect


class GarminClient:
    def __init__(self):
        # No credentials stored in constructor
        self.client = None
        self._authenticated = False
        self.mfa_ticket_dict = None

    def _is_mfa_required(self, exception: Exception) -> bool:
        """Check if exception indicates MFA is required."""
        if isinstance(exception, AttributeError):
            return "'dict' object has no attribute 'expired'" in str(exception)
        elif isinstance(exception, garminconnect.GarminConnectAuthenticationError):
            return "MFA-required" in str(exception) or "Authentication failed" in str(exception)
        return False
    
    def _handle_mfa_required(self) -> None:
        """Handle MFA requirement by capturing ticket and raising exception."""
        if hasattr(self.client.garth, 'oauth2_token') and isinstance(self.client.garth.oauth2_token, dict):
            self.mfa_ticket_dict = self.client.garth.oauth2_token
            logger.info(f"MFA ticket captured: {self.mfa_ticket_dict}")
            raise MFARequiredException(message="MFA code is required.", mfa_data=self.mfa_ticket_dict)
        else:
            logger.error("MFA detected but oauth2_token is not a dict. This is unexpected.")
            raise Exception("MFA detection failed: Invalid token format")

    async def authenticate(self, email: str, password: str):
        """Clean authentication with simplified exception handling."""
        # Use credentials immediately, don't store them
        self.client = garminconnect.Garmin(email, password)
        del email, password  # Clear from memory after use

        try:
            def login_wrapper():
                return self.client.login()
            
            await asyncio.get_event_loop().run_in_executor(None, login_wrapper)
            self._authenticated = True
            self.mfa_ticket_dict = None
            
        except Exception as e:
            # Check if this is an MFA-related error
            if self._is_mfa_required(e):
                self._handle_mfa_required()
            else:
                # Convert to our standard authentication error
                raise garminconnect.GarminConnectAuthenticationError(f"Authentication failed: {str(e)}") from e




    async def _fetch_hrv_data(self, target_date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetches HRV data for the given date."""
        # logger.info(f"Attempting to fetch HRV data for {target_date_iso}")
        try:
            hrv_data = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_hrv_data, target_date_iso
            )
            logger.debug(f"Raw HRV data for {target_date_iso}: {hrv_data}")
            return hrv_data
        except Exception as e:
            logger.error(f"Error fetching HRV data for {target_date_iso}: {str(e)}")
            return None

    async def _fetch_stats_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch stats and body data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_stats_and_body, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching stats data for {date_iso}: {str(e)}")
            return None

    async def _fetch_sleep_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch sleep data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_sleep_data, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching sleep data for {date_iso}: {str(e)}")
            return None

    async def _fetch_activities_data(self, date_iso: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch activities data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_activities_by_date, date_iso, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching activities data for {date_iso}: {str(e)}")
            return None

    async def _fetch_summary_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch user summary data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_user_summary, date_iso
                )
        except Exception as e:
            logger.error(f"Error fetching summary data for {date_iso}: {str(e)}")
            return None

    async def _fetch_training_status_data(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Fetch training status data for a given date."""
        try:
                return await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_training_status, date_iso
            )
        except Exception as e:
            logger.error(f"Error fetching training status data for {date_iso}: {str(e)}")
            return None

    async def _fetch_raw_data(self, target_date: date) -> Dict[str, Any]:
        """
        Fetch all raw data types concurrently for a given date.
        
        Args:
            target_date: The date to fetch data for
            
        Returns:
            Dictionary containing all raw data types:
            - stats: Stats and body data
            - sleep_data: Sleep data
            - activities: Activities data
            - summary: User summary data
            - training_status: Training status data
            - hrv_payload: HRV data
        """
        date_iso = target_date.isoformat()
        
        # Fetch all data concurrently
        stats, sleep_data, activities, summary, training_status, hrv_payload = await asyncio.gather(
            self._fetch_stats_data(date_iso),
            self._fetch_sleep_data(date_iso),
            self._fetch_activities_data(date_iso),
            self._fetch_summary_data(date_iso),
            self._fetch_training_status_data(date_iso),
            self._fetch_hrv_data(date_iso)
        )

        # Debug logging
        logger.debug(f"Raw stats data: {stats}")
        logger.debug(f"Raw sleep data: {sleep_data}")
        logger.debug(f"Raw activities data: {activities}")
        logger.debug(f"Raw summary data: {summary}")
        logger.debug(f"Raw training status data: {training_status}")
        logger.debug(f"Raw HRV payload: {hrv_payload}")

        return {
            'stats': stats,
            'sleep_data': sleep_data,
            'activities': activities,
            'summary': summary,
            'training_status': training_status,
            'hrv_payload': hrv_payload
        }

    def _process_raw_data_to_metrics(self, target_date: date, raw_data: Dict[str, Any]) -> GarminMetrics:
        """
        Process raw API data into GarminMetrics object.
        
        Args:
            target_date: The date for the metrics
            raw_data: Dictionary containing all raw data types
            
        Returns:
            GarminMetrics object with processed data
        """
        stats = raw_data.get('stats')
        sleep_data = raw_data.get('sleep_data')
        activities = raw_data.get('activities')
        summary = raw_data.get('summary')
        training_status = raw_data.get('training_status')
        hrv_payload = raw_data.get('hrv_payload')
        
        # Process each data type
        hrv_metrics = self._process_hrv_data(hrv_payload, target_date)
        activity_metrics = self._process_activities_data(activities, target_date)
        sleep_metrics = self._process_sleep_data(sleep_data, target_date)
        stats_metrics = self._process_stats_data(stats, target_date)
        summary_metrics = self._process_summary_data(summary, target_date)
        training_metrics = self._process_training_status_data(training_status, target_date)
        
        # Combine all metrics
        return GarminMetrics(
            date=target_date,
            # HRV metrics
            overnight_hrv=hrv_metrics['overnight_hrv'],
            hrv_status=hrv_metrics['hrv_status'],
            # Activity metrics
            all_activity_count=activity_metrics['all_activity_count'],
            running_activity_count=activity_metrics['running_count'],
            running_distance=activity_metrics['running_distance'],
            strength_activity_count=activity_metrics['strength_count'],
            strength_duration=activity_metrics['strength_duration'],
            cardio_activity_count=activity_metrics['cardio_count'],
            cardio_duration=activity_metrics['cardio_duration'],
            # Swimming activity counts
            swim_activity_count=activity_metrics['swim_count'],
            pool_swim_count=activity_metrics['pool_swim'],
            open_water_swim_count=activity_metrics['ows_swim'],
            
            # Swimming distance & duration
            swim_distance_meters=activity_metrics['swim_distance'],
            swim_duration_min=activity_metrics['swim_duration'],
            swim_duration_seconds=activity_metrics['swim_duration_seconds'],
            
            # Swimming laps & lengths
            swim_laps=activity_metrics['swim_laps'],
            active_lengths=activity_metrics['active_lengths'],
            pool_length_meters=activity_metrics['pool_length_meters'],
            
            # Swimming pace & speed
            swim_average_pace_per_100m=activity_metrics['swim_average_pace_per_100m'],
            swim_max_pace_per_100m=activity_metrics['swim_max_pace_per_100m'],
            swim_average_speed=activity_metrics['swim_average_speed'],
            swim_max_speed=activity_metrics['swim_max_speed'],
            
            # Swimming heart rate
            swim_average_hr=activity_metrics['swim_average_hr'],
            swim_max_hr=activity_metrics['swim_max_hr'],
            
            # Swimming strokes & technique
            total_strokes=activity_metrics['total_strokes'],
            swim_average_strokes_per_length=activity_metrics['swim_average_strokes_per_length'],
            swim_average_strokes_per_minute=activity_metrics['swim_average_strokes_per_minute'],
            swim_cadence=activity_metrics['swim_cadence'],
            
            # Swimming efficiency metrics
            avg_swolf=activity_metrics['avg_swolf'],
            min_swolf=activity_metrics['min_swolf'],
            max_swolf=activity_metrics['max_swolf'],
            
            # Swimming zones & intensity
            swim_zone1_time=activity_metrics['swim_zone1_time'],
            swim_zone2_time=activity_metrics['swim_zone2_time'],
            swim_zone3_time=activity_metrics['swim_zone3_time'],
            swim_zone4_time=activity_metrics['swim_zone4_time'],
            swim_zone5_time=activity_metrics['swim_zone5_time'],
            
            # Swimming calories & power
            swim_calories=activity_metrics['swim_calories'],
            swim_training_effect=activity_metrics['swim_training_effect'],
            swim_anaerobic_training_effect=activity_metrics['swim_anaerobic_training_effect'],
            # Sleep metrics
            sleep_score=sleep_metrics['sleep_score'],
            sleep_length=sleep_metrics['sleep_length'],
            # Stats metrics
            weight=stats_metrics['weight'],
            body_fat=stats_metrics['body_fat'],
            blood_pressure_systolic=stats_metrics['blood_pressure_systolic'],
            blood_pressure_diastolic=stats_metrics['blood_pressure_diastolic'],
            # Summary metrics
            active_calories=summary_metrics['active_calories'],
            resting_calories=summary_metrics['resting_calories'],
            intensity_minutes=summary_metrics['intensity_minutes'],
            resting_heart_rate=summary_metrics['resting_heart_rate'],
            average_stress=summary_metrics['average_stress'],
            # Training metrics
            training_status=training_metrics['training_status'],
            vo2max_running=training_metrics['vo2max_running']
        )

    def _process_hrv_data(self, hrv_payload: Optional[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Process HRV data from raw API response."""
        overnight_hrv_value: Optional[int] = None
        hrv_status_value: Optional[str] = None
        
        if hrv_payload:
            hrv_summary = hrv_payload.get('hrvSummary')
            if hrv_summary:
                overnight_hrv_value = hrv_summary.get('lastNightAvg')
                hrv_status_value = hrv_summary.get('status')
            else:
                logger.warning(f"hrvSummary not found in hrv_payload for {target_date}. HRV metrics will be blank.")
        else:
            logger.warning(f"hrv_payload for {target_date} is None. HRV metrics will be blank.")
        
        return {
            'overnight_hrv': overnight_hrv_value,
            'hrv_status': hrv_status_value
        }

    def _process_activities_data(self, activities: Optional[List[Dict[str, Any]]], target_date: date) -> Dict[str, Any]:
        """Process activities data from raw API response."""
        # Initialize counters
        running_count = 0
        running_distance = 0
        strength_count = 0
        strength_duration = 0
        cardio_count = 0
        cardio_duration = 0
        
        # Swimming counters
        swim_count = 0
        pool_swim = 0
        ows_swim = 0
        swim_distance = 0.0
        swim_duration = 0.0
        swim_duration_seconds = 0.0
        swim_laps = 0
        active_lengths = 0
        pool_length_meters = None
        
        # Swimming pace & speed
        swim_average_pace_per_100m = None
        swim_max_pace_per_100m = None
        swim_average_speed = None
        swim_max_speed = None
        
        # Swimming heart rate
        swim_average_hr = None
        swim_max_hr = None
        
        # Swimming strokes & technique
        total_strokes = 0
        swim_average_strokes_per_length = None
        swim_average_strokes_per_minute = None
        swim_cadence = None
        
        # Swimming efficiency metrics
        avg_swolf = None
        min_swolf = None
        max_swolf = None
        
        # Swimming zones & intensity
        swim_zone1_time = None
        swim_zone2_time = None
        swim_zone3_time = None
        swim_zone4_time = None
        swim_zone5_time = None
        
        # Swimming calories & power
        swim_calories = None
        swim_training_effect = None
        swim_anaerobic_training_effect = None

        if activities:
            for activity in activities:
                activity_type = activity.get('activityType', {})
                type_key = activity_type.get('typeKey', '').lower()
                parent_type_id = activity_type.get('parentTypeId')

                if 'run' in type_key or parent_type_id == 1:  # 1 is running
                    running_count += 1
                    running_distance += activity.get('distance', 0) / 1000  # Convert to km
                elif 'strength' in type_key:
                    strength_count += 1
                    strength_duration += activity.get('duration', 0) / 60  # Convert seconds to minutes
                elif 'cardio' in type_key:
                    cardio_count += 1
                    cardio_duration += activity.get('duration', 0) / 60
                if 'swim' in type_key or (parent_type_id == 26 and type_key == 'lap_swimming'):
                    swim_count += 1
                    swim_distance += activity.get('distance', 0)  # Distance is already in meters
                    duration_seconds = activity.get('duration', 0)
                    swim_duration += duration_seconds / 60  # Convert seconds to minutes
                    swim_duration_seconds += duration_seconds
                    swim_laps += activity.get('lapCount', 0)
                    active_lengths += activity.get('activeLengths', 0)
                    
                    # Fix pool length calculation (3333.33m → 33.33m)
                    pool_length = activity.get('poolLength', 0)
                    if pool_length and pool_length > 100:  # If pool length seems too large, divide by 100
                        pool_length_meters = pool_length / 100
                    else:
                        pool_length_meters = pool_length
                    
                    # Swimming pace & speed
                    avg_speed = activity.get('averageSpeed', 0)
                    max_speed = activity.get('maxSpeed', 0)
                    swim_average_speed = avg_speed
                    swim_max_speed = max_speed
                    
                    if avg_speed and avg_speed > 0:
                        swim_average_pace_per_100m = 100 / avg_speed
                    if max_speed and max_speed > 0:
                        swim_max_pace_per_100m = 100 / max_speed
                    
                    # Swimming heart rate
                    swim_max_hr = activity.get('maxHR', 0)
                    swim_average_hr = activity.get('averageHR', 0)
                    
                    # Swimming strokes & technique
                    total_strokes += activity.get('strokes', 0)
                    swim_average_strokes_per_length = activity.get('avgStrokes', 0)
                    swim_average_strokes_per_minute = activity.get('averageSwimCadenceInStrokesPerMinute', 0)
                    swim_cadence = activity.get('swimCadence', 0)
                    
                    # Swimming efficiency metrics
                    avg_swolf = activity.get('averageSwolf', 0)
                    min_swolf = activity.get('minSwolf', 0)
                    max_swolf = activity.get('maxSwolf', 0)
                    
                    # Swimming zones & intensity (if available)
                    swim_zone1_time = activity.get('zone1Time', 0)
                    swim_zone2_time = activity.get('zone2Time', 0)
                    swim_zone3_time = activity.get('zone3Time', 0)
                    swim_zone4_time = activity.get('zone4Time', 0)
                    swim_zone5_time = activity.get('zone5Time', 0)
                    
                    # Swimming calories & power
                    swim_calories = activity.get('calories', 0)
                    swim_training_effect = activity.get('trainingEffect', 0)
                    swim_anaerobic_training_effect = activity.get('anaerobicTrainingEffect', 0)
                    
                    # Determine pool vs open water
                    if 'pool' in type_key or type_key == 'lap_swimming':
                        pool_swim += 1
                    elif 'open' in type_key or 'water' in type_key:
                        ows_swim += 1
        else:
            logger.warning(f"Activities data for {target_date} is None. Activity metrics will be blank.")

        return {
            'all_activity_count': len(activities) if activities is not None else 0,
            'running_count': running_count,
            'running_distance': running_distance,
            'strength_count': strength_count,
            'strength_duration': strength_duration,
            'cardio_count': cardio_count,
            'cardio_duration': cardio_duration,
            
            # Swimming activity counts
            'swim_count': swim_count,
            'pool_swim': pool_swim,
            'ows_swim': ows_swim,
            
            # Swimming distance & duration
            'swim_distance': swim_distance,
            'swim_duration': swim_duration,
            'swim_duration_seconds': swim_duration_seconds,
            
            # Swimming laps & lengths
            'swim_laps': swim_laps,
            'active_lengths': active_lengths,
            'pool_length_meters': pool_length_meters,
            
            # Swimming pace & speed
            'swim_average_pace_per_100m': swim_average_pace_per_100m,
            'swim_max_pace_per_100m': swim_max_pace_per_100m,
            'swim_average_speed': swim_average_speed,
            'swim_max_speed': swim_max_speed,
            
            # Swimming heart rate
            'swim_average_hr': swim_average_hr,
            'swim_max_hr': swim_max_hr,
            
            # Swimming strokes & technique
            'total_strokes': total_strokes,
            'swim_average_strokes_per_length': swim_average_strokes_per_length,
            'swim_average_strokes_per_minute': swim_average_strokes_per_minute,
            'swim_cadence': swim_cadence,
            
            # Swimming efficiency metrics
            'avg_swolf': avg_swolf,
            'min_swolf': min_swolf,
            'max_swolf': max_swolf,
            
            # Swimming zones & intensity
            'swim_zone1_time': swim_zone1_time,
            'swim_zone2_time': swim_zone2_time,
            'swim_zone3_time': swim_zone3_time,
            'swim_zone4_time': swim_zone4_time,
            'swim_zone5_time': swim_zone5_time,
            
            # Swimming calories & power
            'swim_calories': swim_calories,
            'swim_training_effect': swim_training_effect,
            'swim_anaerobic_training_effect': swim_anaerobic_training_effect
        }

    def _process_sleep_data(self, sleep_data: Optional[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Process sleep data from raw API response."""
        sleep_score: Optional[float] = None
        sleep_length: Optional[float] = None
        
        if sleep_data:
            sleep_dto = sleep_data.get('dailySleepDTO', {})
            if sleep_dto:
                sleep_score = sleep_dto.get('sleepScores', {}).get('overall', {}).get('value')
                sleep_time_seconds = sleep_dto.get('sleepTimeSeconds')
                if sleep_time_seconds is not None and sleep_time_seconds > 0:
                    sleep_length = sleep_time_seconds / 3600  # Convert to hours
            else:
                logger.warning(f"Daily sleep DTO not found in sleep data for {target_date}.")
        else:
            logger.warning(f"Sleep data for {target_date} is None. Sleep metrics will be blank.")
        
        return {
            'sleep_score': sleep_score,
            'sleep_length': sleep_length
        }

    def _process_stats_data(self, stats: Optional[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Process stats and body data from raw API response."""
        weight: Optional[float] = None
        body_fat: Optional[float] = None
        blood_pressure_systolic: Optional[int] = None
        blood_pressure_diastolic: Optional[int] = None
        
        if stats:
            weight = stats.get('weight', 0) / 1000 if stats.get('weight') else None  # Convert grams to kg
            body_fat = stats.get('bodyFat')
            blood_pressure_systolic = stats.get('systolic')
            blood_pressure_diastolic = stats.get('diastolic')
        else:
            logger.warning(f"Stats data for {target_date} is None. Weight and body fat metrics will be blank.")
        
        return {
            'weight': weight,
            'body_fat': body_fat,
            'blood_pressure_systolic': blood_pressure_systolic,
            'blood_pressure_diastolic': blood_pressure_diastolic
        }

    def _process_summary_data(self, summary: Optional[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Process user summary data from raw API response."""
        active_calories: Optional[int] = None
        resting_calories: Optional[int] = None
        intensity_minutes: Optional[int] = None
        resting_heart_rate: Optional[int] = None
        average_stress: Optional[int] = None
        
        if summary:
            active_calories = summary.get('activeKilocalories')
            resting_calories = summary.get('bmrKilocalories')
            intensity_minutes = (summary.get('moderateIntensityMinutes', 0) or 0) + (2 * (summary.get('vigorousIntensityMinutes', 0) or 0))
            resting_heart_rate = summary.get('restingHeartRate')
            average_stress = summary.get('averageStressLevel')
        else:
            logger.warning(f"User summary data for {target_date} is None. Summary metrics will be blank.")
        
        return {
            'active_calories': active_calories,
            'resting_calories': resting_calories,
            'intensity_minutes': intensity_minutes,
            'resting_heart_rate': resting_heart_rate,
            'average_stress': average_stress
        }

    def _process_training_status_data(self, training_status: Optional[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Process training status data from raw API response."""
        vo2max_running: Optional[float] = None
        training_status_phrase: Optional[str] = None
        
        if training_status:
            most_recent_vo2max = training_status.get('mostRecentVO2Max')
            if most_recent_vo2max:
                generic_vo2max = most_recent_vo2max.get('generic')
                if generic_vo2max:
                    vo2max_running = generic_vo2max.get('vo2MaxValue')

            training_status_data = {}
            most_recent_training_status = training_status.get('mostRecentTrainingStatus')
            if most_recent_training_status:
                latest_training_status_data = most_recent_training_status.get('latestTrainingStatusData')
                if latest_training_status_data:
                    training_status_data = latest_training_status_data
            
            first_device = None
            if training_status_data:
                for value in training_status_data.values():
                    first_device = value
                    break
            
            if first_device:
                training_status_phrase = first_device.get('trainingStatusFeedbackPhrase')
        else:
            logger.warning(f"Training status data for {target_date} is None. VO2 Max and training status metrics will be blank.")
        
        return {
            'vo2max_running': vo2max_running,
            'training_status': training_status_phrase
        }

    async def get_metrics(self, target_date: date, email: str, password: str) -> GarminMetrics:
        """Get metrics for a specific date. Re-authenticates each time for security."""
        logger.debug(f"VERIFY get_metrics: display_name: {getattr(self.client, 'display_name', 'Not Set')}, oauth2_token type: {type(self.client.garth.oauth2_token)}")
        
        # Re-authenticate each time for security (credentials not stored)
        await self.authenticate(email, password)

        try:
            # Use our new _fetch_raw_data method for clean data fetching
            raw_data = await self._fetch_raw_data(target_date)
            
            # Process the raw data into GarminMetrics
            return self._process_raw_data_to_metrics(target_date, raw_data)

        except Exception as e:
            logger.error(f"Error fetching metrics for {target_date}: {str(e)}")
            # Return metrics object with just the date and potentially HRV if fetched before error
            return GarminMetrics(
                date=target_date,
                overnight_hrv=locals().get('overnight_hrv_value'), # Use locals() to get value if available
                hrv_status=locals().get('hrv_status_value')
            )


    async def submit_mfa_code(self, mfa_code: str):
        """Submits the MFA code to complete authentication."""
        if not hasattr(self, 'mfa_ticket_dict') or not self.mfa_ticket_dict:
            logger.error("MFA ticket (dict state) not available. Cannot submit MFA code.")
            raise Exception("MFA ticket (dict state) not available. Please authenticate first.")

        try:
            loop = asyncio.get_event_loop()
            # The resume_login function from garth.sso expects the garth.Client instance
            # that is awaiting MFA, and the MFA code.
            resume_login_result = await loop.run_in_executor(
                None,
                lambda: resume_login(self.mfa_ticket_dict, mfa_code) # Use the captured dict
            )
            
            logger.info(f"DEBUG: resume_login returned type: {type(resume_login_result)}")
            logger.info(f"DEBUG: resume_login returned value: {resume_login_result}")

            if isinstance(resume_login_result, tuple) and len(resume_login_result) == 2:
                oauth1_token, oauth2_token = resume_login_result
                logger.info(f"DEBUG: Unpacked OAuth1Token: {type(oauth1_token)}, {oauth1_token}")
                logger.info(f"DEBUG: Unpacked OAuth2Token: {type(oauth2_token)}, {oauth2_token}")
            else:
                logger.error(f"CRITICAL: resume_login did not return the expected tuple of tokens. Returned: {resume_login_result}")
                raise Exception("MFA token processing failed: Unexpected result from resume_login.")

            if 'client' in self.mfa_ticket_dict and isinstance(self.mfa_ticket_dict.get('client'), garth.Client):
                garth_client_instance = self.mfa_ticket_dict['client']
                logger.info(f"DEBUG: Retrieved garth_client_instance from mfa_ticket_dict: {type(garth_client_instance)}")
                
                # Explicitly set the new tokens on the garth.Client instance
                garth_client_instance.oauth1_token = oauth1_token
                garth_client_instance.oauth2_token = oauth2_token
                logger.info("DEBUG: Successfully set oauth1_token and oauth2_token on garth_client_instance.")
                logger.info(f"DEBUG: garth_client_instance.oauth2_token after update: {type(garth_client_instance.oauth2_token)}, {garth_client_instance.oauth2_token}")

                # Now, assign this updated garth_client_instance to self.client.garth
                self.client.garth = garth_client_instance
                logger.info("Successfully updated self.client.garth with the token-updated garth_client_instance from mfa_ticket_dict.")

                # New logic to populate profile details on self.client:
                try:
                    logger.info("Attempting to fetch profile details via self.client.garth.profile...")
                    # Accessing self.client.garth.profile should trigger garth to fetch it if not already cached,
                    # using the now-authenticated garth client.
                    profile_data = self.client.garth.profile
                    
                    if profile_data:
                        self.client.display_name = profile_data.get("displayName")
                        self.client.full_name = profile_data.get("fullName")
                        self.client.unit_system = profile_data.get("measurementSystem")
                        logger.info(f"Successfully populated profile details. Display name: {self.client.display_name}, Full name: {self.client.full_name}, Unit system: {self.client.unit_system}")
                    else:
                        logger.error("Failed to retrieve profile_data from self.client.garth.profile (it was None or empty).")
                        raise Exception("Failed to retrieve profile data after MFA.")

                except Exception as e_profile_fetch:
                    logger.error(f"Error fetching/setting profile details after MFA: {e_profile_fetch}", exc_info=True)
                    # This is critical for subsequent API calls, so re-raise.
                    raise Exception(f"Failed to fetch or set profile details after MFA: {e_profile_fetch}")
            else:
                logger.error(f"CRITICAL: Failed to find a valid garth.Client in self.mfa_ticket_dict['client'] after resume_login. mfa_ticket_dict['client'] is: {self.mfa_ticket_dict.get('client')}")
                raise Exception("Critical error: Could not retrieve garth.Client instance from mfa_ticket_dict post MFA for token update.")
            
            self._authenticated = True
            self.mfa_ticket_dict = None # Clear the used MFA ticket dict
            logger.info("MFA verification successful. Garth client updated with authenticated instance.")
            return True
        except (garminconnect.GarminConnectAuthenticationError, garth.exc.GarthException) as e: # Corrected to GarthException
            self._authenticated = False
            logger.error(f"MFA code submission failed: {str(e)}")
            raise Exception(f"MFA code submission failed: {str(e)}")
        except Exception as e:
            self._authenticated = False
            logger.error(f"An unexpected error occurred during MFA submission: {str(e)}")

    async def get_metrics_for_date_range(self, start_date: date, end_date: date, email: str, password: str) -> List[GarminMetrics]:
        """
        Fetch metrics for a date range. Re-authenticates each time for security.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range  
            email: Garmin email
            password: Garmin password
            
        Returns:
            List of GarminMetrics objects for each date in the range
            
        Raises:
            Exception: If no metrics are fetched for any date
        """
        from datetime import timedelta
        
        logger.info(f"Fetching metrics from {start_date} to {end_date}")
        metrics = []
        current_date = start_date
        
        while current_date <= end_date:
            logger.info(f"Fetching metrics for {current_date}")
            daily_metrics = await self.get_metrics(current_date, email, password)
            if daily_metrics:
                metrics.append(daily_metrics)
            current_date += timedelta(days=1)
        
        if not metrics:
            logger.warning("No metrics fetched from Garmin for the date range.")
            raise Exception("No metrics data found for the selected date range.")
        
        logger.info(f"Successfully fetched {len(metrics)} days of metrics")
        return metrics

    async def authenticate_with_bitwarden(self, user_profile_name: str):
        """
        Authenticate with Garmin using credentials retrieved from Bitwarden.
        
        Args:
            user_profile_name (str): The name of the user profile in Bitwarden
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            BitwardenAuthenticationError: If Bitwarden authentication fails
            BitwardenItemNotFoundError: If credentials not found in Bitwarden
            AuthenticationError: If Garmin authentication fails
        """
        try:
            from .bitwarden_client import BitwardenClient, BitwardenAuthenticationError, BitwardenItemNotFoundError
            
            # Initialize Bitwarden client
            bitwarden_client = BitwardenClient()
            
            # Authenticate with Bitwarden
            logger.info(f"Authenticating with Bitwarden for user profile: {user_profile_name}")
            bitwarden_client.authenticate()
            
            # Retrieve credentials from Bitwarden
            logger.info(f"Retrieving credentials from Bitwarden for: {user_profile_name}")
            credentials = bitwarden_client.get_credentials(user_profile_name)
            
            # Extract username and password
            username = credentials.get('username')
            password = credentials.get('password')
            
            if not username or not password:
                raise BitwardenItemNotFoundError(f"Incomplete credentials for {user_profile_name}: missing username or password")
            
            logger.info(f"Successfully retrieved credentials for {user_profile_name} from Bitwarden")
            
            # Authenticate with Garmin using the retrieved credentials
            logger.info(f"Authenticating with Garmin using Bitwarden credentials for {user_profile_name}")
            await self.authenticate(username, password)
            
            # Clean up Bitwarden session
            bitwarden_client.logout()
            
            logger.info(f"Successfully authenticated with Garmin using Bitwarden credentials for {user_profile_name}")
            return True
            
        except (BitwardenAuthenticationError, BitwardenItemNotFoundError) as e:
            logger.error(f"Bitwarden error during authentication: {str(e)}")
            raise

    async def get_swimming_session_details(self, activity_id: int, email: str, password: str) -> Dict[str, Any]:
        """
        Get detailed swimming session data including intervals, laps, and lengths.
        
        Args:
            activity_id: Garmin activity ID
            email: Garmin email
            password: Garmin password
            
        Returns:
            Dictionary containing detailed swimming session data
        """
        # Authenticate
        await self.authenticate(email, password)
        
        try:
            # Fetch detailed data using the new API methods we discovered
            splits_data = self.client.get_activity_splits(activity_id)
            split_summaries = self.client.get_activity_split_summaries(activity_id)
            typed_splits = self.client.get_activity_typed_splits(activity_id)
            
            logger.info(f"Successfully fetched detailed swimming data for activity {activity_id}")
            
            return {
                'splits_data': splits_data,
                'split_summaries': split_summaries,
                'typed_splits': typed_splits
            }
            
        except Exception as e:
            logger.error(f"Error fetching detailed swimming data for activity {activity_id}: {e}")
            raise

    async def get_swimming_activities_with_details(self, target_date: date, email: str, password: str) -> List[Dict[str, Any]]:
        """
        Get swimming activities for a date with detailed interval data.
        
        Args:
            target_date: Date to fetch activities for
            email: Garmin email
            password: Garmin password
            
        Returns:
            List of swimming activities with detailed data
        """
        # Authenticate
        await self.authenticate(email, password)
        
        try:
            # Get activities for the date
            activities = self.client.get_activities_by_date(target_date, target_date)
            
            swimming_activities = []
            for activity in activities:
                if activity.get('activityType', {}).get('typeKey') == 'lap_swimming':
                    activity_id = activity['activityId']
                    
                    # Get detailed data for this swimming activity
                    detailed_data = await self.get_swimming_session_details(activity_id, email, password)
                    
                    # Combine basic activity data with detailed data
                    swimming_activity = {
                        'basic_data': activity,
                        'detailed_data': detailed_data
                    }
                    swimming_activities.append(swimming_activity)
            
            logger.info(f"Found {len(swimming_activities)} swimming activities for {target_date}")
            return swimming_activities
            
        except Exception as e:
            logger.error(f"Error fetching swimming activities for {target_date}: {e}")
            raise


