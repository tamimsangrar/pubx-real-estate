#!/usr/bin/env python3
"""
Debug script to test SELECT policy specifically
"""

import os
import requests
import json
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def decode_jwt(token):
    """Decode JWT to see the role"""
    try:
        # Decode without verification to see the payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        return f"Error decoding JWT: {e}"

def test_select_with_details():
    """Test SELECT with detailed debugging"""
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not all([supabase_url, anon_key, service_key]):
        print("❌ Missing environment variables")
        return
    
    # Remove trailing slash
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    print("🔍 Debugging SELECT Policy")
    print("=" * 50)
    
    # Decode JWT tokens to see roles
    print("📋 JWT Token Analysis:")
    anon_decoded = decode_jwt(anon_key)
    service_decoded = decode_jwt(service_key)
    
    print(f"ANON Key Role: {anon_decoded.get('role', 'NOT FOUND')}")
    print(f"SERVICE Key Role: {service_decoded.get('role', 'NOT FOUND')}")
    print(f"ANON Key Claims: {json.dumps(anon_decoded, indent=2)}")
    
    # Test SELECT with anon key
    print("\n🔍 Testing SELECT with ANON key...")
    api_url = f"{supabase_url}/rest/v1/leads?select=*&limit=1"
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("❌ ANON key can SELECT (this should be blocked)")
            data = response.json()
            print(f"   Returned {len(data)} rows")
        elif response.status_code in [401, 403]:
            print("✅ ANON key correctly blocked from SELECT")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test SELECT with service key (should work)
    print("\n🔍 Testing SELECT with SERVICE key...")
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SERVICE key can SELECT (this is correct)")
            data = response.json()
            print(f"   Returned {len(data)} rows")
        else:
            print(f"❌ SERVICE key cannot SELECT: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test with different endpoint to see if it's a general issue
    print("\n🔍 Testing SELECT on settings table...")
    api_url_settings = f"{supabase_url}/rest/v1/settings?select=*&limit=1"
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url_settings, headers=headers)
        
        print(f"Settings SELECT Status: {response.status_code}")
        
        if response.status_code == 200:
            print("❌ ANON can also SELECT from settings (should be blocked)")
        elif response.status_code in [401, 403]:
            print("✅ ANON correctly blocked from settings SELECT")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    test_select_with_details()
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Steps:")
    print("1. Check if your anon key has the correct role")
    print("2. Verify RLS is properly enforced")
    print("3. Check if there are any default policies")
    print("4. Try forcing RLS: ALTER TABLE leads FORCE ROW LEVEL SECURITY;")

if __name__ == "__main__":
    main() 