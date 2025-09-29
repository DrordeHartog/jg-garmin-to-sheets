from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional, List
import asyncio
import logging
import garminconnect
import json
from garth.sso import resume_login
import garth
from src.exceptions import MFARequiredException

logger = logging.getLogger(__name__)

# GarminMetrics class removed - processing will be done in Cache → Raw DB jobs


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
        Assumes client is already authenticated.
        
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

    async def fetch_raw_data_for_date(self, target_date: date) -> Dict[str, Any]:
        """
        Fetch raw data for a specific date with authentication.
        This is the main method that jobs should call.
        
        Args:
            target_date: The date to fetch data for
            
        Returns:
            Dictionary containing all raw data types
            
        Raises:
            ValueError: If credentials are not available
            Exception: If authentication or data fetching fails
        """
        # Get credentials from environment
        import os
        email = os.getenv('GARMIN_EMAIL')
        password = os.getenv('GARMIN_PASSWORD')
        
        if not email or not password:
            raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD environment variables must be set")
        
        # Authenticate
        await self.authenticate(email, password)
        
        # Fetch raw data
        return await self._fetch_raw_data(target_date)

# Processing methods removed - will be implemented in Cache → Raw DB jobs

# Individual processing methods removed - will be implemented in Cache → Raw DB jobs

# All processing methods removed - will be implemented in Cache → Raw DB jobs

# All processing and high-level methods removed - will be implemented in Cache → Raw DB jobs


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

# High-level methods that depend on processing removed - will be implemented in Cache → Raw DB jobs

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

# Swimming-specific methods removed - will be implemented in Cache → Raw DB jobs


