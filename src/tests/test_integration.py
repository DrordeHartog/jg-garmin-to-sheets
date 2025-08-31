import asyncio
from datetime import date
from src.garmin_client import GarminClient

async def test_garmin_integration():
    print('Testing Garmin + Bitwarden integration...')
    
    try:
        # Initialize Garmin client (empty credentials initially)
        client = GarminClient("", "")
        print('✓ GarminClient initialized')
        
        # Authenticate using Bitwarden
        print('\nAuthenticating with Garmin using Bitwarden credentials...')
        await client.authenticate_with_bitwarden('Garmin User1')
        print('✓ Garmin authentication successful')
        
        # Test getting metrics
        print('\nTesting metrics retrieval...')
        metrics = await client.get_metrics(date.today())
        print(f'✓ Metrics retrieved successfully')
        print(f'  Sleep Score: {metrics.sleep_score}')
        print(f'  HRV: {metrics.overnight_hrv}')
        
        print('\n🎉 Full integration test completed successfully!')
        
    except Exception as e:
        print(f'\n❌ Error: {e}')

# Run the test
asyncio.run(test_garmin_integration())
