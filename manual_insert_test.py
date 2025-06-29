#!/usr/bin/env python3
"""
Manual insert test to debug anon key issues
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_manual_insert():
    """Test manual insert using direct HTTP requests"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not anon_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return
    
    # Remove trailing slash if present
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    # Construct the API endpoint
    api_url = f"{supabase_url}/rest/v1/leads"
    
    # Headers for anon key
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Test data
    test_data = {
        "name": "Manual Test User",
        "email": "manual@test.com",
        "phone": "+1234567890",
        "source": "manual_test"
    }
    
    print("🔍 Testing manual insert with anon key...")
    print(f"URL: {api_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(api_url, headers=headers, json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Manual insert successful!")
            return True
        else:
            print("❌ Manual insert failed!")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_service_insert():
    """Test service role insert for comparison"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return
    
    # Remove trailing slash if present
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    # Construct the API endpoint
    api_url = f"{supabase_url}/rest/v1/leads"
    
    # Headers for service key
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Test data
    test_data = {
        "name": "Service Test User",
        "email": "service@test.com",
        "phone": "+1234567890",
        "source": "manual_test"
    }
    
    print("\n🔍 Testing manual insert with service key...")
    print(f"URL: {api_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(api_url, headers=headers, json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Service insert successful!")
            return True
        else:
            print("❌ Service insert failed!")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_keys():
    """Check if the API keys are properly formatted"""
    print("🔍 Checking API keys...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"ANON_KEY (first 20 chars): {anon_key[:20] if anon_key else 'NOT SET'}...")
    print(f"SERVICE_KEY (first 20 chars): {service_key[:20] if service_key else 'NOT SET'}...")
    
    # Check if keys look like Supabase keys
    if anon_key and not anon_key.startswith('eyJ'):
        print("⚠️  ANON_KEY doesn't look like a valid JWT token")
    
    if service_key and not service_key.startswith('eyJ'):
        print("⚠️  SERVICE_KEY doesn't look like a valid JWT token")
    
    if supabase_url and not supabase_url.startswith('https://'):
        print("⚠️  SUPABASE_URL should start with https://")

def main():
    """Run all tests"""
    print("🔧 Manual Insert Test")
    print("=" * 50)
    
    check_keys()
    
    print("\n" + "=" * 50)
    anon_success = test_manual_insert()
    
    print("\n" + "=" * 50)
    service_success = test_service_insert()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   Anon insert: {'✅ Success' if anon_success else '❌ Failed'}")
    print(f"   Service insert: {'✅ Success' if service_success else '❌ Failed'}")
    
    if not anon_success and service_success:
        print("\n🔧 Troubleshooting:")
        print("   1. Check your ANON_KEY in .env file")
        print("   2. Make sure it's the 'anon public' key from Supabase")
        print("   3. Verify RLS policies in Supabase dashboard")
        print("   4. Try the SQL fix script in Supabase SQL Editor")

if __name__ == "__main__":
    main() 