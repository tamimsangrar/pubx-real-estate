#!/usr/bin/env python3
"""
Test script for Module A - Supabase Backend
Run this to verify your database setup is working correctly.
"""

import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def test_database_connection():
    """Test basic database connection"""
    print("🔍 Testing database connection...")
    try:
        # Test a simple query
        response = supabase.table('settings').select('*').limit(1).execute()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_leads_table():
    """Test leads table operations"""
    print("\n🔍 Testing leads table...")
    
    # Test inserting a lead
    test_lead = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "source": "test"
    }
    
    try:
        response = supabase.table('leads').insert(test_lead).execute()
        lead_id = response.data[0]['id']
        print(f"✅ Lead inserted successfully with ID: {lead_id}")
        
        # Test reading the lead
        response = supabase.table('leads').select('*').eq('id', lead_id).execute()
        if response.data:
            print("✅ Lead read successfully")
            return lead_id
        else:
            print("❌ Failed to read lead")
            return None
            
    except Exception as e:
        print(f"❌ Leads table test failed: {e}")
        return None

def test_lead_scoring(lead_id):
    """Test lead scoring functionality"""
    if not lead_id:
        print("❌ Skipping lead scoring test - no lead ID")
        return
    
    print(f"\n🔍 Testing lead scoring for lead: {lead_id}")
    
    try:
        # Manually insert a lead score
        test_score = {
            "lead_id": lead_id,
            "score": 85,
            "reason": "Valid email, phone number, and recent engagement"
        }
        
        response = supabase.table('lead_scores').insert(test_score).execute()
        score_id = response.data[0]['id']
        print(f"✅ Lead score inserted successfully with ID: {score_id}")
        
        # Test reading the score
        response = supabase.table('lead_scores').select('*').eq('lead_id', lead_id).execute()
        if response.data:
            print(f"✅ Lead score read successfully: {response.data[0]['score']}/100")
            return True
        else:
            print("❌ Failed to read lead score")
            return False
            
    except Exception as e:
        print(f"❌ Lead scoring test failed: {e}")
        return False

def test_settings_table():
    """Test settings table operations"""
    print("\n🔍 Testing settings table...")
    
    try:
        # Test reading settings
        response = supabase.table('settings').select('*').execute()
        if response.data:
            print(f"✅ Settings read successfully. Found {len(response.data)} settings:")
            for setting in response.data:
                print(f"   - {setting['key']}: {setting['value_json']}")
            return True
        else:
            print("❌ No settings found")
            return False
            
    except Exception as e:
        print(f"❌ Settings table test failed: {e}")
        return False

def test_rls_policies():
    """Test Row Level Security policies"""
    print("\n🔍 Testing RLS policies...")
    
    # Test with anon key (should only be able to insert leads)
    anon_supabase = create_client(supabase_url, os.getenv("SUPABASE_ANON_KEY"))
    
    try:
        # Test insert (should work)
        test_lead_anon = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1987654321",
            "source": "anon_test"
        }
        
        # Use the same approach as the working manual test
        response = anon_supabase.table('leads').insert(test_lead_anon).execute()
        print("✅ Anon user can insert leads (RLS working correctly)")
        
        # Test select (should fail)
        try:
            response = anon_supabase.table('leads').select('*').limit(1).execute()
            print("❌ Anon user can read leads (RLS not working correctly)")
        except Exception as e:
            if "42501" in str(e) or "row-level security" in str(e).lower():
                print("✅ Anon user cannot read leads (RLS working correctly)")
            else:
                print(f"❌ Unexpected error when testing anon read: {e}")
            
    except Exception as e:
        if "42501" in str(e) or "row-level security" in str(e).lower():
            print("❌ Anon user cannot insert leads (RLS policy issue)")
            print("   This might be because:")
            print("   1. RLS policies are not properly configured")
            print("   2. The anon key doesn't have the right permissions")
            print("   3. The policy needs to be updated")
            print("   Note: Manual HTTP test worked, so this might be a client library issue")
        else:
            print(f"❌ RLS test failed with unexpected error: {e}")

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Delete test leads (this will cascade to lead_scores)
        response = supabase.table('leads').delete().eq('source', 'test').execute()
        response2 = supabase.table('leads').delete().eq('source', 'anon_test').execute()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Module A - Supabase Backend Tests")
    print("=" * 50)
    
    # Run tests
    if not test_database_connection():
        return
    
    test_settings_table()
    lead_id = test_leads_table()
    test_lead_scoring(lead_id)
    test_rls_policies()
    
    # Cleanup
    cleanup_test_data()
    
    print("\n" + "=" * 50)
    print("🎉 Module A testing completed!")
    print("\nNext steps:")
    print("1. Set up your API keys in .env file")
    print("2. Run: python test_db.py")
    print("3. If all tests pass, proceed to Module B (Chat Orchestrator)")

if __name__ == "__main__":
    main() 