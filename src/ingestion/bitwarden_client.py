import subprocess
import json
import logging
import os
from typing import Dict, Optional, List
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class BitwardenAuthenticationError(Exception):
    """Raised when Bitwarden authentication fails."""
    pass

class BitwardenItemNotFoundError(Exception):
    """Raised when a requested item is not found in Bitwarden."""
    pass

class BitwardenClient:
    """
    A secure client for interacting with Bitwarden CLI to retrieve credentials.
    Uses passkey authentication for secure access to stored credentials.
    """
    
    def __init__(self):
        self._check_bitwarden_cli()
        self._session_key = None
    
    def _check_bitwarden_cli(self):
        """Check if Bitwarden CLI is installed and accessible."""
        try:
            result = subprocess.run(['bw', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError('Bitwarden CLI is not properly installed')
            logger.info(f"Bitwarden CLI version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError('Bitwarden CLI is not installed. Please install it first.')
    
    def _check_if_already_authenticated(self) -> bool:
        """Check if Bitwarden is already unlocked and we can access items."""
        try:
            # Check if we can list items without authentication
            result = subprocess.run(
                ['bw', 'list', 'items'],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Bitwarden using passkey.
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            BitwardenAuthenticationError: If authentication fails
        """
        try:
            # First, check if we're already authenticated
            if self._check_if_already_authenticated():
                logger.info("Bitwarden is already unlocked and accessible")
                return True
            
            # Check if we have a session key in environment
            if 'BW_SESSION' in os.environ:
                self._session_key = os.environ['BW_SESSION']
                logger.info("Using existing BW_SESSION from environment")
                return True
            
            # If not authenticated, we need to unlock
            logger.info("Bitwarden is locked. Please unlock it manually first:")
            logger.info("Run: bw unlock")
            logger.info("Then run this script again.")
            
            raise BitwardenAuthenticationError(
                "Bitwarden is locked. Please unlock it manually with 'bw unlock' first."
            )
            
        except subprocess.CalledProcessError as e:
            raise BitwardenAuthenticationError(f"Bitwarden CLI error: {e}")
        except Exception as e:
            raise BitwardenAuthenticationError(f"Authentication failed: {e}")
    
    def get_credentials(self, item_name: str) -> Dict[str, str]:
        """
        Retrieve credentials for a specific item from Bitwarden.
        
        Args:
            item_name (str): The name of the item in Bitwarden
            
        Returns:
            Dict[str, str]: Dictionary containing username and password
            
        Raises:
            BitwardenAuthenticationError: If not authenticated
            BitwardenItemNotFoundError: If item not found
        """
        try:
            # List all items to find the one we want
            result = subprocess.run(
                ['bw', 'list', 'items'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                raise BitwardenAuthenticationError(f"Failed to list items: {result.stderr}")
            
            items = json.loads(result.stdout)
            
            # Find the item by name
            target_item = None
            for item in items:
                if item.get('name') == item_name:
                    target_item = item
                    break
            
            if not target_item:
                raise BitwardenItemNotFoundError(f"Item '{item_name}' not found in Bitwarden")
            
            # Extract login credentials
            login = target_item.get('login', {})
            username = login.get('username', '')
            password = login.get('password', '')
            
            if not username or not password:
                raise BitwardenItemNotFoundError(f"Incomplete credentials for '{item_name}': missing username or password")
            
            return {
                'username': username,
                'password': password
            }
            
        except json.JSONDecodeError as e:
            raise BitwardenAuthenticationError(f"Failed to parse Bitwarden response: {e}")
        except Exception as e:
            raise BitwardenAuthenticationError(f"Failed to retrieve credentials: {e}")
    
    def logout(self):
        """Logout and clear the session key."""
        if self._session_key:
            try:
                subprocess.run(['bw', 'lock'], capture_output=True)
                logger.info("Logged out of Bitwarden")
            except Exception as e:
                logger.warning(f"Error during logout: {e}")
            finally:
                self._session_key = None