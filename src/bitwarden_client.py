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
                                  capture_output=True, text=True, check=True)
            logger.info(f"Bitwarden CLI version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise BitwardenAuthenticationError(
                "Bitwarden CLI not found. Please install it from: "
                "https://bitwarden.com/help/cli/"
            )
    
    def authenticate(self) -> bool:
        """
        Authenticate with Bitwarden using passkey.
        Returns True if authentication successful.
        """
        try:
            # Check if already authenticated
            if self._session_key:
                return True
            
            # Try to unlock with passkey
            logger.info("Authenticating with Bitwarden...")
            result = subprocess.run(
                ['bw', 'unlock', '--passwordenv', 'BW_PASSWORD'],
                capture_output=True, text=True, env=os.environ
            )
            
            if result.returncode == 0:
                # Extract session key from output
                for line in result.stdout.split('
'):
                    if 'BW_SESSION=' in line:
                        self._session_key = line.split('=')[1].strip()
                        logger.info("Successfully authenticated with Bitwarden")
                        return True
            
            # If password env not set, prompt for passkey
            logger.info("Please authenticate with your Bitwarden passkey...")
            result = subprocess.run(
                ['bw', 'unlock'],
                capture_output=True, text=True, input='
'  # This will prompt for passkey
            )
            
            if result.returncode == 0:
                # Extract session key
                for line in result.stdout.split('
'):
                    if 'BW_SESSION=' in line:
                        self._session_key = line.split('=')[1].strip()
                        logger.info("Successfully authenticated with Bitwarden")
                        return True
            
            raise BitwardenAuthenticationError("Failed to authenticate with Bitwarden")
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise BitwardenAuthenticationError(f"Authentication failed: {e}")
    
    def get_credentials(self, item_name: str) -> Dict[str, str]:
        """
        Retrieve credentials for a specific item from Bitwarden.
        
        Args:
            item_name: Name of the item in Bitwarden vault
            
        Returns:
            Dictionary containing username, password, and other fields
        """
        if not self.authenticate():
            raise BitwardenAuthenticationError("Authentication required")
        
        try:
            # Search for the item
            result = subprocess.run(
                ['bw', 'list', 'items', '--search', item_name],
                capture_output=True, text=True, check=True,
                env={'BW_SESSION': self._session_key}
            )
            
            items = json.loads(result.stdout)
            
            if not items:
                raise BitwardenItemNotFoundError(f"Item '{item_name}' not found in Bitwarden")
            
            # Get the first matching item
            item = items[0]
            
            # Extract credentials
            credentials = {
                'username': item.get('login', {}).get('username', ''),
                'password': item.get('login', {}).get('password', ''),
                'name': item.get('name', ''),
                'id': item.get('id', '')
            }
            
            # Add any custom fields
            if 'fields' in item.get('login', {}):
                for field in item['login']['fields']:
                    credentials[field.get('name', '')] = field.get('value', '')
            
            logger.info(f"Retrieved credentials for '{item_name}'")
            return credentials
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Bitwarden CLI error: {e}")
            raise BitwardenAuthenticationError(f"Failed to retrieve credentials: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise BitwardenAuthenticationError(f"Invalid response from Bitwarden: {e}")
    
    def store_credentials(self, item_name: str, username: str, password: str, 
                         additional_fields: Optional[Dict[str, str]] = None) -> bool:
        """
        Store credentials in Bitwarden.
        
        Args:
            item_name: Name for the item
            username: Username/email
            password: Password
            additional_fields: Additional fields to store
            
        Returns:
            True if successful
        """
        if not self.authenticate():
            raise BitwardenAuthenticationError("Authentication required")
        
        try:
            # Create item data
            item_data = {
                "type": 1,  # Login type
                "name": item_name,
                "login": {
                    "username": username,
                    "password": password
                }
            }
            
            # Add custom fields if provided
            if additional_fields:
                item_data["login"]["fields"] = []
                for key, value in additional_fields.items():
                    item_data["login"]["fields"].append({
                        "name": key,
                        "value": value,
                        "type": 0  # Text field
                    })
            
            # Create temporary file for item data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(item_data, f)
                temp_file = f.name
            
            try:
                # Create the item
                result = subprocess.run(
                    ['bw', 'create', 'item', '--file', temp_file],
                    capture_output=True, text=True, check=True,
                    env={'BW_SESSION': self._session_key}
                )
                
                logger.info(f"Successfully stored credentials for '{item_name}'")
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            raise BitwardenAuthenticationError(f"Failed to store credentials: {e}")
    
    def list_items(self, search_term: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List items in Bitwarden vault.
        
        Args:
            search_term: Optional search term to filter items
            
        Returns:
            List of item dictionaries
        """
        if not self.authenticate():
            raise BitwardenAuthenticationError("Authentication required")
        
        try:
            cmd = ['bw', 'list', 'items']
            if search_term:
                cmd.extend(['--search', search_term])
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True,
                env={'BW_SESSION': self._session_key}
            )
            
            items = json.loads(result.stdout)
            
            # Extract basic info
            item_list = []
            for item in items:
                item_info = {
                    'name': item.get('name', ''),
                    'username': item.get('login', {}).get('username', ''),
                    'id': item.get('id', '')
                }
                item_list.append(item_info)
            
            return item_list
            
        except Exception as e:
            logger.error(f"Failed to list items: {e}")
            raise BitwardenAuthenticationError(f"Failed to list items: {e}")
    
    def logout(self):
        """Logout and clear session."""
        if self._session_key:
            try:
                subprocess.run(['bw', 'lock'], check=True)
            except:
                pass  # Ignore errors during logout
            finally:
                self._session_key = setup_logging()
                logger.info("Logged out of Bitwarden")
