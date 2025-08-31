# Bitwarden Integration Setup Guide

This guide explains how to set up and use the Bitwarden integration for secure credential management in GarminGo.

## Prerequisites

1. **Bitwarden Account**: You need a Bitwarden account with passkey authentication enabled
2. **Bitwarden CLI**: Install the Bitwarden CLI tool

## Installation

### 1. Install Bitwarden CLI

**macOS (using Homebrew):**
```bash
brew install bitwarden-cli
```

**Linux:**
```bash
# Download from https://github.com/bitwarden/cli/releases
# Or use your package manager
```

**Windows:**
```bash
# Download from https://github.com/bitwarden/cli/releases
# Or use Chocolatey: choco install bitwarden-cli
```

### 2. Verify Installation
```bash
bw --version
```

## Setup

### 1. Store Your Garmin Credentials in Bitwarden

1. **Log into Bitwarden** (web app or desktop app)
2. **Create a new Login item** with these details:
   - **Name**: `Garmin User1` (or whatever name you prefer)
   - **Username**: Your Garmin email
   - **Password**: Your Garmin password
   - **URL**: `https://connect.garmin.com`

### 2. Test Bitwarden CLI Authentication

```bash
# Test authentication with your passkey
bw unlock
```

You should be prompted for your Bitwarden passkey (fingerprint, face ID, or PIN).

## Usage

### Option 1: Use Bitwarden Integration (Recommended)

The new Bitwarden integration allows you to authenticate without storing credentials in plain text:

```python
from src.garmin_client import GarminClient

# Initialize client (credentials will be retrieved from Bitwarden)
garmin_client = GarminClient("", "")

# Authenticate using Bitwarden
await garmin_client.authenticate_with_bitwarden("Garmin User1")

# Now you can use the client normally
metrics = await garmin_client.get_metrics(date.today())
```

### Option 2: Traditional .env Method (Still Available)

You can still use the traditional method with credentials stored in `.env` file:

```bash
# .env file
USER1_GARMIN_EMAIL=your.email@example.com
USER1_GARMIN_PASSWORD=your_password
USER1_SHEET_ID=your_google_sheet_id
```

## Security Benefits

1. **No Plain Text Passwords**: Credentials are never stored in plain text files
2. **Passkey Authentication**: Uses your Bitwarden passkey for secure access
3. **Automatic Cleanup**: Session keys are automatically cleared after use
4. **Centralized Management**: All credentials managed in Bitwarden vault

## Troubleshooting

### Bitwarden CLI Not Found
```bash
# Make sure Bitwarden CLI is in your PATH
which bw
```

### Authentication Issues
```bash
# Test Bitwarden authentication manually
bw unlock
bw list items
```

### Credentials Not Found
- Ensure the item name in Bitwarden matches what you're using in the code
- Check that the item has both username and password fields populated

## Migration from .env Method

To migrate from the traditional `.env` method to Bitwarden:

1. **Store your credentials in Bitwarden** (see Setup step 1)
2. **Update your code** to use `authenticate_with_bitwarden()` instead of the traditional method
3. **Remove credentials from .env** file (optional, for security)
4. **Test the new authentication flow**

## Example Integration

Here's how the integration works in practice:

```python
import asyncio
from datetime import date
from src.garmin_client import GarminClient

async def main():
    # Initialize client
    client = GarminClient("", "")
    
    try:
        # Authenticate with Bitwarden
        await client.authenticate_with_bitwarden("Garmin User1")
        
        # Get today's metrics
        metrics = await client.get_metrics(date.today())
        print(f"Sleep score: {metrics.sleep_score}")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(main())
```

## Security Notes

- **Session Management**: Bitwarden sessions are automatically managed and cleaned up
- **Error Handling**: The integration includes comprehensive error handling for authentication failures
- **Logging**: All authentication attempts are logged for security auditing
- **MFA Support**: The integration supports Garmin's MFA when required

