-- Complete RLS Policy Fix for Module A
-- Run this in your Supabase SQL Editor

-- First, disable RLS temporarily to clean up
ALTER TABLE leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE lead_scores DISABLE ROW LEVEL SECURITY;
ALTER TABLE settings DISABLE ROW LEVEL SECURITY;
ALTER TABLE listings DISABLE ROW LEVEL SECURITY;
ALTER TABLE lead_notes DISABLE ROW LEVEL SECURITY;

-- Drop ALL existing policies to start fresh
DROP POLICY IF EXISTS "Anonymous users can insert leads" ON leads;
DROP POLICY IF EXISTS "Service role has full access to leads" ON leads;
DROP POLICY IF EXISTS "Users can read leads" ON leads;

DROP POLICY IF EXISTS "Service role has full access to lead_scores" ON lead_scores;
DROP POLICY IF EXISTS "Users can read lead_scores" ON lead_scores;

DROP POLICY IF EXISTS "Service role has full access to settings" ON settings;
DROP POLICY IF EXISTS "Users can read settings" ON settings;

DROP POLICY IF EXISTS "Service role has full access to listings" ON listings;
DROP POLICY IF EXISTS "Anyone can read listings" ON listings;

DROP POLICY IF EXISTS "Service role has full access to lead_notes" ON lead_notes;
DROP POLICY IF EXISTS "Users can read lead_notes" ON lead_notes;

-- Re-enable RLS
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_notes ENABLE ROW LEVEL SECURITY;

-- Recreate policies for leads table (most important)
-- 1. Service role - full access
CREATE POLICY "service_role_full_access_leads" ON leads
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- 2. Anonymous users - insert only
CREATE POLICY "anon_insert_leads" ON leads
    FOR INSERT TO anon
    WITH CHECK (true);

-- 3. Authenticated users - read only
CREATE POLICY "auth_read_leads" ON leads
    FOR SELECT TO authenticated
    USING (true);

-- Recreate policies for lead_scores table
CREATE POLICY "service_role_full_access_lead_scores" ON lead_scores
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "auth_read_lead_scores" ON lead_scores
    FOR SELECT TO authenticated
    USING (true);

-- Recreate policies for settings table
CREATE POLICY "service_role_full_access_settings" ON settings
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "auth_read_settings" ON settings
    FOR SELECT TO authenticated
    USING (true);

-- Recreate policies for listings table
CREATE POLICY "service_role_full_access_listings" ON listings
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "anon_read_listings" ON listings
    FOR SELECT TO anon
    USING (true);

-- Recreate policies for lead_notes table
CREATE POLICY "service_role_full_access_lead_notes" ON lead_notes
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "auth_read_lead_notes" ON lead_notes
    FOR SELECT TO authenticated
    USING (true);

-- Verify policies were created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename IN ('leads', 'lead_scores', 'settings', 'listings', 'lead_notes')
ORDER BY tablename, policyname;

-- Test the policies
-- This should work with service role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Service Test', 'service@test.com', '+1234567890', 'test');

-- This should work with anon role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Anon Test', 'anon@test.com', '+1234567890', 'test');

-- This should fail with anon role
-- SELECT * FROM leads LIMIT 1; 