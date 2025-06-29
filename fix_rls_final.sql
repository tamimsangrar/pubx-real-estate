-- Final RLS Fix - Idempotent Version
-- Run this in your Supabase SQL Editor

-- 1. Check for any default policies that might be allowing anon SELECT
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
WHERE tablename IN ('leads', 'settings', 'lead_scores', 'listings', 'lead_notes')
ORDER BY tablename, policyname;

-- 2. Check if there are any policies for 'public' role
SELECT 
    schemaname,
    tablename,
    policyname,
    roles
FROM pg_policies 
WHERE 'public' = ANY(roles) OR 'anon' = ANY(roles)
ORDER BY tablename, policyname;

-- 3. Force RLS on all tables
ALTER TABLE leads FORCE ROW LEVEL SECURITY;
ALTER TABLE lead_scores FORCE ROW LEVEL SECURITY;
ALTER TABLE settings FORCE ROW LEVEL SECURITY;
ALTER TABLE listings FORCE ROW LEVEL SECURITY;
ALTER TABLE lead_notes FORCE ROW LEVEL SECURITY;

-- 4. Drop any policies that might be allowing anon SELECT or are duplicates
DROP POLICY IF EXISTS "anon_select_leads" ON leads;
DROP POLICY IF EXISTS "anon_select_settings" ON settings;
DROP POLICY IF EXISTS "anon_select_lead_scores" ON lead_scores;
DROP POLICY IF EXISTS "anon_select_listings" ON listings;
DROP POLICY IF EXISTS "anon_select_lead_notes" ON lead_notes;

DROP POLICY IF EXISTS "public_select_leads" ON leads;
DROP POLICY IF EXISTS "public_select_settings" ON settings;
DROP POLICY IF EXISTS "public_select_lead_scores" ON lead_scores;
DROP POLICY IF EXISTS "public_select_listings" ON listings;
DROP POLICY IF EXISTS "public_select_lead_notes" ON lead_notes;

-- 5. Drop and recreate correct policies for leads table
DROP POLICY IF EXISTS "service_role_full_access_leads" ON leads;
CREATE POLICY "service_role_full_access_leads" ON leads
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "anon_insert_leads" ON leads;
CREATE POLICY "anon_insert_leads" ON leads
    FOR INSERT TO anon
    WITH CHECK (true);

DROP POLICY IF EXISTS "auth_read_leads" ON leads;
CREATE POLICY "auth_read_leads" ON leads
    FOR SELECT TO authenticated
    USING (true);

-- 6. Drop and recreate correct policies for settings table
DROP POLICY IF EXISTS "service_role_full_access_settings" ON settings;
CREATE POLICY "service_role_full_access_settings" ON settings
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "auth_read_settings" ON settings;
CREATE POLICY "auth_read_settings" ON settings
    FOR SELECT TO authenticated
    USING (true);

-- 7. Verify the final policies
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
WHERE tablename IN ('leads', 'settings')
ORDER BY tablename, policyname;

-- 8. Test the policies
-- This should work with service role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Service Test', 'service@test.com', '+1234567890', 'test');

-- This should work with anon role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Anon Test', 'anon@test.com', '+1234567890', 'test');

-- This should FAIL with anon role (no policy for anon SELECT)
-- SELECT * FROM leads LIMIT 1; 