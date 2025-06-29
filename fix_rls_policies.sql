-- Fix RLS Policies for Module A
-- Run this in your Supabase SQL Editor

-- First, drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Anonymous users can insert leads" ON leads;
DROP POLICY IF EXISTS "Service role has full access to leads" ON leads;
DROP POLICY IF EXISTS "Users can read leads" ON leads;

-- Recreate policies in the correct order
-- 1. Service role policy (most permissive first)
CREATE POLICY "Service role has full access to leads" ON leads
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- 2. Anonymous insert policy
CREATE POLICY "Anonymous users can insert leads" ON leads
    FOR INSERT TO anon
    WITH CHECK (true);

-- 3. Authenticated read policy
CREATE POLICY "Users can read leads" ON leads
    FOR SELECT TO authenticated
    USING (true);

-- Verify RLS is enabled
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Test the policies
-- This should work with service role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Test', 'test@test.com', '+1234567890', 'test');

-- This should work with anon role
-- INSERT INTO leads (name, email, phone, source) VALUES ('Anon Test', 'anon@test.com', '+1234567890', 'anon_test');

-- This should fail with anon role
-- SELECT * FROM leads LIMIT 1; 