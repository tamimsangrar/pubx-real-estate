-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Try to enable pgvector, but don't fail if it's not available
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS "pgvector";
EXCEPTION
    WHEN OTHERS THEN
        -- Log the error but continue
        RAISE NOTICE 'pgvector extension not available, continuing without vector search capabilities';
END $$;

-- Create leads table
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    source TEXT DEFAULT 'chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create lead_scores table
CREATE TABLE lead_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create settings table
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT UNIQUE NOT NULL,
    value_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create listings table (embedding column commented out; enable if pgvector is available)
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL,
    price DECIMAL(12,2),
    url TEXT,
    description TEXT,
    -- embedding vector(1536), -- Uncomment if pgvector is available
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create lead_notes table for voice transcripts
CREATE TABLE lead_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    source TEXT DEFAULT 'voice',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_lead_scores_lead_id ON lead_scores(lead_id);
CREATE INDEX idx_lead_scores_score ON lead_scores(score);

-- (Vector index creation commented out; enable if pgvector is available)
-- DO $$
-- BEGIN
--     CREATE INDEX idx_listings_embedding ON listings USING ivfflat (embedding vector_cosine_ops);
-- EXCEPTION
--     WHEN OTHERS THEN
--         RAISE NOTICE 'Could not create vector index, pgvector may not be available';
-- END $$;

-- Enable Row Level Security
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_notes ENABLE ROW LEVEL SECURITY;

-- RLS Policies for leads table
-- Anonymous users can only insert leads
CREATE POLICY "Anonymous users can insert leads" ON leads
    FOR INSERT TO anon
    WITH CHECK (true);

-- Service role has full access
CREATE POLICY "Service role has full access to leads" ON leads
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can read their own leads (for admin dashboard)
CREATE POLICY "Users can read leads" ON leads
    FOR SELECT TO authenticated
    USING (true);

-- RLS Policies for lead_scores table
CREATE POLICY "Service role has full access to lead_scores" ON lead_scores
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can read lead_scores" ON lead_scores
    FOR SELECT TO authenticated
    USING (true);

-- RLS Policies for settings table
CREATE POLICY "Service role has full access to settings" ON settings
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can read settings" ON settings
    FOR SELECT TO authenticated
    USING (true);

-- RLS Policies for listings table
CREATE POLICY "Service role has full access to listings" ON listings
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Anyone can read listings" ON listings
    FOR SELECT TO anon
    USING (true);

-- RLS Policies for lead_notes table
CREATE POLICY "Service role has full access to lead_notes" ON lead_notes
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can read lead_notes" ON lead_notes
    FOR SELECT TO authenticated
    USING (true);

-- Insert default settings
INSERT INTO settings (key, value_json) VALUES
('system_prompt', '{"value": "You are a helpful real estate agent assistant. Help visitors find properties and capture leads professionally."}'),
('lead_score_threshold', '{"value": 70}'),
('chat_welcome_message', '{"value": "Hi! I\'m your AI real estate assistant. How can I help you find your perfect home today?"}');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 