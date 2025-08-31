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
    
    def authenticate(self) -> bool:
        """
        Authenticate with Bitwarden using passkey.
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            BitwardenAuthenticationError: If authentication fails
        """
        try:
            # Try to unlock with passkey
            logger.info("Authenticating with Bitwarden...")
            result = subprocess.run(
                ['bw', 'unlock', '--passwordenv', 'BW_PASSWORD'],
                capture_output=True, text=True, env=os.environ
            )
            
            if result.returncode == 0:
                # Extract session key from output
                for line in result.stdout.split('\n'):
                    if 'BW_SESSION=' in line:
                        self._session_key = line.split('=')[1].strip()
                        logger.info("Successfully authenticated with Bitwarden")
                        return True
            
            # If password env not set, prompt for passkey
            logger.info("Please authenticate with your Bitwarden passkey...")
            result = subprocess.run(
                ['bw', 'unlock'],
                capture_output=True, text=True, input='\n'
            )
            
            if result.returncode == 0:
                # Extract session key from output
                for line in result.stdout.split('\n'):
                    if 'BW_SESSION=' in line:
                        self._session_key = line.split('=')[1].strip()
                        logger.info("Successfully authenticated with Bitwarden")
                        return True
            
            # If we get here, authentication failed
            raise BitwardenAuthenticationError(f"Authentication failed: {result.stderr}")
            
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
        if not self._session_key:
            raise BitwardenAuthenticationError("Not authenticated. Call authenticate() first.")
        
        try:
            # Set the session key for this command
            env = os.environ.copy()
            env['BW_SESSION'] = self._session_key
            
            # List all items to find the one we want
            result = subprocess.run(
                ['bw', 'list', 'items'],
                capture_output=True, text=True, env=env
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
                env = os.environ.copy()
                env['BW_SESSION'] = self._session_key
                subprocess.run(['bw', 'lock'], capture_output=True, env=env)
                logger.info("Logged out of Bitwarden")
            except Exception as e:
                logger.warning(f"Error during logout: {e}")
            finally:
                self._session_key = None
