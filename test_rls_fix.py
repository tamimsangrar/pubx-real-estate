#!/usr/bin/env python3
"""
Simple RLS test after policy fix
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anon_insert():
    """Test anonymous insert"""
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not anon_key:
        print("❌ Missing environment variables")
        return False
    
    # Remove trailing slash
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    api_url = f"{supabase_url}/rest/v1/leads"
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    test_data = {
        "name": "RLS Fix Test",
        "email": "rls@test.com",
        "phone": "+1234567890",
        "source": "rls_test"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=test_data)
        
        if response.status_code == 201:
            print("✅ Anonymous insert successful!")
            return True
        else:
            print(f"❌ Anonymous insert failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_anon_read():
    """Test anonymous read (should fail)"""
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not anon_key:
        print("❌ Missing environment variables")
        return False
    
    # Remove trailing slash
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    api_url = f"{supabase_url}/rest/v1/leads?select=*&limit=1"
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Anonymous read correctly blocked!")
            return True
        else:
            print(f"❌ Anonymous read should have been blocked: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def cleanup():
    """Clean up test data"""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        return
    
    # Remove trailing slash
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    api_url = f"{supabase_url}/rest/v1/leads?source=eq.rls_test"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 200:
            print("🧹 Test data cleaned up")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    print("🔧 Testing RLS Policies After Fix")
    print("=" * 40)
    
    # Test anon insert
    insert_success = test_anon_insert()
    
    # Test anon read (should fail)
    read_blocked = test_anon_read()
    
    # Cleanup
    cleanup()
    
    print("\n" + "=" * 40)
    print("📋 Results:")
    print(f"   Anon insert: {'✅ Success' if insert_success else '❌ Failed'}")
    print(f"   Anon read blocked: {'✅ Success' if read_blocked else '❌ Failed'}")
    
    if insert_success and read_blocked:
        print("\n🎉 RLS policies are working correctly!")
        print("Module A is ready for production!")
    else:
        print("\n❌ RLS policies still need fixing")
        print("Run the fix_rls_complete.sql script in Supabase SQL Editor")

if __name__ == "__main__":
    main() 