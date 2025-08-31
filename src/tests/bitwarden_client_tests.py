import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import json
import tempfile
import os
from pathlib import Path

# Import the modules to test
from src.bitwarden_client import BitwardenClient, BitwardenAuthenticationError, BitwardenItemNotFoundError
from src.garmin_client import GarminClient
from src.exceptions import AuthenticationError

class TestBitwardenClient(unittest.TestCase):
    """Test cases for BitwardenClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bitwarden_client = BitwardenClient()
    
    @patch('subprocess.run')
    def test_check_bitwarden_cli_success(self, mock_run):
        """Test successful Bitwarden CLI check."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '2024.1.0'
        
        # Should not raise an exception
        self.bitwarden_client._check_bitwarden_cli()
        mock_run.assert_called_once_with(['bw', '--version'], 
                                        capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_check_bitwarden_cli_not_installed(self, mock_run):
        """Test Bitwarden CLI not installed."""
        mock_run.side_effect = FileNotFoundError('bw: command not found')
        
        with self.assertRaises(RuntimeError) as context:
            self.bitwarden_client._check_bitwarden_cli()
        
        self.assertIn('Bitwarden CLI is not installed', str(context.exception))
    
    @patch('subprocess.run')
    def test_authenticate_success(self, mock_run):
        """Test successful authentication."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'session_key_here'
        
        result = self.bitwarden_client.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(self.bitwarden_client._session_key, 'session_key_here')
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_authenticate_failure(self, mock_run):
        """Test authentication failure."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = 'Invalid passkey'
        
        with self.assertRaises(BitwardenAuthenticationError) as context:
            self.bitwarden_client.authenticate()
        
        self.assertIn('Authentication failed', str(context.exception))
    
    @patch('subprocess.run')
    def test_get_credentials_success(self, mock_run):
        """Test successful credential retrieval."""
        # Mock authentication
        self.bitwarden_client._session_key = 'test_session'
        
        # Mock item list response
        mock_items = [
            {
                'id': 'item1',
                'name': 'Garmin User1',
                'login': {
                    'username': 'test@example.com',
                    'password': 'testpass123'
                }
            }
        ]
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_items)
        
        credentials = self.bitwarden_client.get_credentials('Garmin User1')
        
        self.assertEqual(credentials['username'], 'test@example.com')
        self.assertEqual(credentials['password'], 'testpass123')
    
    @patch('subprocess.run')
    def test_get_credentials_item_not_found(self, mock_run):
        """Test credential retrieval when item not found."""
        self.bitwarden_client._session_key = 'test_session'
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '[]'
        
        with self.assertRaises(BitwardenItemNotFoundError) as context:
            self.bitwarden_client.get_credentials('NonExistentUser')
        
        self.assertIn('not found in Bitwarden', str(context.exception))
    
    @patch('subprocess.run')
    def test_get_credentials_not_authenticated(self, mock_run):
        """Test credential retrieval without authentication."""
        with self.assertRaises(BitwardenAuthenticationError) as context:
            self.bitwarden_client.get_credentials('test_user')
        
        self.assertIn('Not authenticated', str(context.exception))
    
    def test_logout(self):
        """Test logout functionality."""
        self.bitwarden_client._session_key = 'test_session'
        
        self.bitwarden_client.logout()
        
        self.assertIsNone(self.bitwarden_client._session_key)

class TestGarminClientWithBitwarden(unittest.TestCase):
    """Test cases for GarminClient integration with Bitwarden."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.garmin_client = GarminClient()
    
    @patch('src.bitwarden_client.BitwardenClient')
    def test_authenticate_with_bitwarden_success(self, mock_bitwarden_class):
        """Test successful Garmin authentication using Bitwarden credentials."""
        # Mock Bitwarden client
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.get_credentials.return_value = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        # Mock successful Garmin authentication
        with patch.object(self.garmin_client, '_authenticate_garmin') as mock_auth:
            mock_auth.return_value = True
            
            result = self.garmin_client.authenticate_with_bitwarden('Garmin User1')
            
            self.assertTrue(result)
            mock_bitwarden.authenticate.assert_called_once()
            mock_bitwarden.get_credentials.assert_called_once_with('Garmin User1')
            mock_auth.assert_called_once_with('test@example.com', 'testpass123')
    
    @patch('src.bitwarden_client.BitwardenClient')
    def test_authenticate_with_bitwarden_bitwarden_failure(self, mock_bitwarden_class):
        """Test Garmin authentication when Bitwarden authentication fails."""
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.authenticate.side_effect = BitwardenAuthenticationError('Auth failed')
        
        with self.assertRaises(BitwardenAuthenticationError):
            self.garmin_client.authenticate_with_bitwarden('Garmin User1')
    
    @patch('src.bitwarden_client.BitwardenClient')
    def test_authenticate_with_bitwarden_garmin_failure(self, mock_bitwarden_class):
        """Test Garmin authentication when Garmin authentication fails."""
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.get_credentials.return_value = {
            'username': 'test@example.com',
            'password': 'wrongpass'
        }
        
        with patch.object(self.garmin_client, '_authenticate_garmin') as mock_auth:
            mock_auth.side_effect = AuthenticationError('Invalid credentials')
            
            with self.assertRaises(AuthenticationError):
                self.garmin_client.authenticate_with_bitwarden('Garmin User1')
    
    @patch('src.bitwarden_client.BitwardenClient')
    def test_authenticate_with_bitwarden_credentials_not_found(self, mock_bitwarden_class):
        """Test Garmin authentication when credentials not found in Bitwarden."""
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.get_credentials.side_effect = BitwardenItemNotFoundError('Not found')
        
        with self.assertRaises(BitwardenItemNotFoundError):
            self.garmin_client.authenticate_with_bitwarden('NonExistentUser')

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete Bitwarden + Garmin flow."""
    
    @patch('src.bitwarden_client.BitwardenClient')
    @patch('src.garmin_client.GarminClient')
    def test_complete_workflow_success(self, mock_garmin_class, mock_bitwarden_class):
        """Test the complete workflow from Bitwarden to Garmin data retrieval."""
        # Mock Bitwarden client
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.get_credentials.return_value = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        # Mock Garmin client
        mock_garmin = mock_garmin_class.return_value
        mock_garmin.authenticate_with_bitwarden.return_value = True
        
        # Mock health data
        mock_health_data = {
            'sleep_score': 85,
            'hrv': 45,
            'weight': 70.5
        }
        mock_garmin.get_health_data.return_value = mock_health_data
        
        # Test the workflow
        bitwarden_client = BitwardenClient()
        garmin_client = GarminClient()
        
        # Authenticate with Bitwarden
        bitwarden_client.authenticate()
        credentials = bitwarden_client.get_credentials('Garmin User1')
        
        # Authenticate with Garmin
        garmin_client.authenticate_with_bitwarden('Garmin User1')
        
        # Get health data
        health_data = garmin_client.get_health_data()
        
        # Verify the flow
        self.assertEqual(credentials['username'], 'test@example.com')
        self.assertEqual(health_data['sleep_score'], 85)
        
        # Verify cleanup
        bitwarden_client.logout()
    
    @patch('src.bitwarden_client.BitwardenClient')
    def test_error_handling_and_cleanup(self, mock_bitwarden_class):
        """Test proper error handling and cleanup in case of failures."""
        mock_bitwarden = mock_bitwarden_class.return_value
        mock_bitwarden.authenticate.return_value = True
        mock_bitwarden.get_credentials.side_effect = Exception('Unexpected error')
        
        bitwarden_client = BitwardenClient()
        
        try:
            bitwarden_client.authenticate()
            credentials = bitwarden_client.get_credentials('Garmin User1')
        except Exception:
            # Ensure cleanup happens even on error
            bitwarden_client.logout()
        
        # Verify logout was called
        mock_bitwarden.logout.assert_called_once()

class TestSecurityFeatures(unittest.TestCase):
    """Test security features of the Bitwarden integration."""
    
    def test_session_key_cleanup(self):
        """Test that session keys are properly cleaned up."""
        client = BitwardenClient()
        client._session_key = 'test_session_key'
        
        # Verify session key is set
        self.assertEqual(client._session_key, 'test_session_key')
        
        # Logout should clear the session key
        client.logout()
        self.assertIsNone(client._session_key)
    
    @patch('subprocess.run')
    def test_credentials_not_stored_in_memory(self, mock_run):
        """Test that credentials are not stored in memory after use."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'session_key'
        
        client = BitwardenClient()
        client.authenticate()
        
        # Mock credential retrieval
        mock_run.return_value.stdout = json.dumps([{
            'id': 'item1',
            'name': 'Garmin User1',
            'login': {
                'username': 'test@example.com',
                'password': 'testpass123'
            }
        }])
        
        credentials = client.get_credentials('Garmin User1')
        
        # Verify credentials were retrieved
        self.assertEqual(credentials['username'], 'test@example.com')
        
        # Verify they are not stored in the client object
        self.assertFalse(hasattr(client, '_credentials'))
        self.assertFalse(hasattr(client, '_username'))
        self.assertFalse(hasattr(client, '_password'))

if __name__ == '__main__':
    unittest.main()
