#!/usr/bin/env python3
"""
Debug script to check RLS policies and permissions
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase clients
supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
anon_key = os.getenv("SUPABASE_ANON_KEY")

if not all([supabase_url, service_key, anon_key]):
    print("❌ Error: Missing required environment variables")
    exit(1)

service_client = create_client(supabase_url, service_key)
anon_client = create_client(supabase_url, anon_key)

def check_rls_status():
    """Check if RLS is enabled on tables"""
    print("🔍 Checking RLS status on tables...")
    
    try:
        # Check if RLS is enabled on leads table
        response = service_client.rpc('check_rls_status', {'table_name': 'leads'}).execute()
        print("✅ RLS status check completed")
    except Exception as e:
        print(f"⚠️  Could not check RLS status via RPC: {e}")
        print("   This is normal if the function doesn't exist")

def check_policies():
    """Check existing policies"""
    print("\n🔍 Checking existing policies...")
    
    try:
        # Try to get policies (this might not work with Supabase client)
        print("   Note: Policy checking via client is limited")
        print("   Check your Supabase dashboard: Authentication > Policies")
    except Exception as e:
        print(f"   Error checking policies: {e}")

def test_anon_insert():
    """Test anonymous insert with detailed error"""
    print("\n🔍 Testing anonymous insert with detailed error...")
    
    test_lead = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "source": "debug_test"
    }
    
    try:
        response = anon_client.table('leads').insert(test_lead).execute()
        print("✅ Anonymous insert successful!")
        return response.data[0]['id']
    except Exception as e:
        print(f"❌ Anonymous insert failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return None

def test_service_insert():
    """Test service role insert"""
    print("\n🔍 Testing service role insert...")
    
    test_lead = {
        "name": "Service Test User",
        "email": "service@example.com",
        "phone": "+1234567890",
        "source": "debug_test"
    }
    
    try:
        response = service_client.table('leads').insert(test_lead).execute()
        print("✅ Service role insert successful!")
        return response.data[0]['id']
    except Exception as e:
        print(f"❌ Service role insert failed: {e}")
        return None

def check_table_structure():
    """Check table structure"""
    print("\n🔍 Checking table structure...")
    
    try:
        # Try to get table info
        response = service_client.table('leads').select('*').limit(1).execute()
        print("✅ Table structure looks good")
        return True
    except Exception as e:
        print(f"❌ Table structure issue: {e}")
        return False

def main():
    """Run all diagnostics"""
    print("🔧 RLS Debug Diagnostics")
    print("=" * 50)
    
    check_table_structure()
    check_rls_status()
    check_policies()
    
    # Test inserts
    anon_id = test_anon_insert()
    service_id = test_service_insert()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   Anonymous insert: {'✅ Success' if anon_id else '❌ Failed'}")
    print(f"   Service insert: {'✅ Success' if service_id else '❌ Failed'}")
    
    if not anon_id and service_id:
        print("\n🔧 Troubleshooting:")
        print("   1. Check Supabase dashboard: Authentication > Policies")
        print("   2. Ensure 'Anonymous users can insert leads' policy exists")
        print("   3. Verify the policy has 'WITH CHECK (true)'")
        print("   4. Try recreating the policy manually in the dashboard")
    
    # Cleanup
    if anon_id or service_id:
        print("\n🧹 Cleaning up test data...")
        try:
            service_client.table('leads').delete().eq('source', 'debug_test').execute()
            print("✅ Cleanup successful")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    main() 