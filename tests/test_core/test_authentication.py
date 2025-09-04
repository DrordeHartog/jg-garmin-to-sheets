"""
Tests for the refactored authentication logic in GarminClient.
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from src.core.garmin_client import GarminClient
from src.exceptions import MFARequiredException


class TestGarminClientAuthentication:
    """Test the refactored authentication methods."""
    
    @pytest.mark.asyncio
    async def test_authenticate_with_real_credentials(self):
        """Test authentication with actual Garmin credentials - INTEGRATION TEST FIRST."""
        from dotenv import load_dotenv
        load_dotenv()

        client = GarminClient()
        
        # Use real credentials from environment
        email = os.getenv("USER1_GARMIN_EMAIL")
        password = os.getenv("USER1_GARMIN_PASSWORD")
        
        # Debug output
        print(f"DEBUG: Email found: {email is not None}")
        print(f"DEBUG: Password found: {password is not None}")
        print(f"DEBUG: Email value: {email}")
        
        if not email or not password:
            pytest.skip("Real Garmin credentials not available in environment")
        
        try:
            await client.authenticate(email, password)
            
            # Should be authenticated
            assert client._authenticated is True
            assert client.client is not None
            assert client.client.display_name is not None
            
            print(f"✅ Successfully authenticated with real credentials for: {client.client.display_name}")
            
        except MFARequiredException:
            # MFA is required - this is also a valid test result
            assert client.mfa_ticket_dict is not None
            print("⚠️ MFA required - test passed but needs manual MFA code")
            pytest.skip("MFA required - test passed but needs manual MFA code")
        
        except Exception as e:
            pytest.fail(f"Authentication failed with real credentials: {e}")
    
    
    def test_is_mfa_required_attribute_error(self):
        """Test MFA detection for AttributeError."""
        client = GarminClient()
        
        # Test MFA-related AttributeError
        mfa_error = AttributeError("'dict' object has no attribute 'expired'")
        assert client._is_mfa_required(mfa_error) is True
        
        # Test non-MFA AttributeError
        other_error = AttributeError("'NoneType' object has no attribute 'login'")
        assert client._is_mfa_required(other_error) is False
    
    def test_is_mfa_required_garmin_error(self):
        """Test MFA detection for GarminConnectAuthenticationError."""
        client = GarminClient()
        
        # Test MFA-related errors
        mfa_error1 = Exception("MFA-required for this account")
        mfa_error2 = Exception("Authentication failed - MFA needed")
        
        # Mock the GarminConnectAuthenticationError
        with patch('src.core.garmin_client.garminconnect') as mock_garmin:
            mock_garmin.GarminConnectAuthenticationError = Exception
            
            assert client._is_mfa_required(mfa_error1) is True
            assert client._is_mfa_required(mfa_error2) is True
            
            # Test non-MFA error
            other_error = Exception("Invalid credentials")
            assert client._is_mfa_required(other_error) is False
    
    def test_handle_mfa_required_success(self):
        """Test successful MFA handling."""
        client = GarminClient()
        
        # Mock the client with MFA ticket
        mock_client = Mock()
        mock_client.garth = Mock()
        mock_client.garth.oauth2_token = {"ticket": "test_ticket"}
        client.client = mock_client
        
        # Should raise MFARequiredException with ticket data
        with pytest.raises(MFARequiredException) as exc_info:
            client._handle_mfa_required()
        
        assert exc_info.value.mfa_data == {"ticket": "test_ticket"}
        assert client.mfa_ticket_dict == {"ticket": "test_ticket"}
    
    def test_handle_mfa_required_invalid_token(self):
        """Test MFA handling with invalid token format."""
        client = GarminClient()
        
        # Mock the client with invalid token
        mock_client = Mock()
        mock_client.garth = Mock()
        mock_client.garth.oauth2_token = "invalid_token"  # Not a dict
        client.client = mock_client
        
        # Should raise generic exception
        with pytest.raises(Exception) as exc_info:
            client._handle_mfa_required()
        
        assert "MFA detection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful authentication."""
        client = GarminClient()
        
        # Mock successful login
        with patch('src.core.garmin_client.garminconnect') as mock_garmin:
            mock_garmin_client = Mock()
            mock_garmin_client.login.return_value = True
            mock_garmin.Garmin.return_value = mock_garmin_client
            
            # Mock the executor
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(return_value=True)
                
                await client.authenticate("test@example.com", "password123")
                
                # Should be authenticated
                assert client._authenticated is True
                assert client.mfa_ticket_dict is None
                assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_mfa_required(self):
        """Test authentication when MFA is required."""
        client = GarminClient()
        
        # Mock MFA-required error
        with patch('src.core.garmin_client.garminconnect') as mock_garmin:
            mock_garmin_client = Mock()
            mock_garmin_client.login.side_effect = AttributeError("'dict' object has no attribute 'expired'")
            mock_garmin_client.garth = Mock()
            mock_garmin_client.garth.oauth2_token = {"ticket": "mfa_ticket"}
            mock_garmin.Garmin.return_value = mock_garmin_client
            
            # Mock the executor
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(side_effect=AttributeError("'dict' object has no attribute 'expired'"))
                
                # Should raise MFARequiredException
                with pytest.raises(MFARequiredException) as exc_info:
                    await client.authenticate("test@example.com", "password123")
                
                assert exc_info.value.mfa_data == {"ticket": "mfa_ticket"}
    
