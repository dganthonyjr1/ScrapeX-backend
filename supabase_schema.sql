-- Supabase Schema for ScrapeX Job Storage
-- This schema stores all scraping jobs and results in the database
-- Prevents data loss and enables job tracking

-- Jobs table: stores all scraping jobs
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    type TEXT NOT NULL, -- 'scrape', 'bulk_scrape', 'directory_scrape'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Request parameters
    directory_url TEXT,
    business_url TEXT,
    business_urls TEXT[], -- for bulk scrape
    max_businesses INTEGER,
    max_pages INTEGER DEFAULT 10,
    batch_size INTEGER DEFAULT 50,
    
    -- Progress tracking
    total_to_process INTEGER,
    processed_count INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    
    -- Results
    result JSONB,
    error_message TEXT,
    
    -- Resource tracking
    memory_used_mb FLOAT,
    duration_seconds FLOAT,
    
    -- Metadata
    metadata JSONB
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_created_at ON scraping_jobs(created_at DESC);

-- Business data table: stores scraped business information
CREATE TABLE IF NOT EXISTS scraped_businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id TEXT REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    
    -- Business information
    business_name TEXT,
    business_type TEXT,
    website TEXT,
    phone TEXT[],
    email TEXT[],
    address TEXT,
    description TEXT,
    
    -- Owner information
    owner_names TEXT[],
    owner_emails TEXT[],
    owner_linkedin TEXT[],
    
    -- Additional data
    services TEXT[],
    social_media JSONB,
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_directory TEXT,
    raw_data JSONB
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_scraped_businesses_job_id ON scraped_businesses(job_id);
CREATE INDEX IF NOT EXISTS idx_scraped_businesses_user_id ON scraped_businesses(user_id);
CREATE INDEX IF NOT EXISTS idx_scraped_businesses_website ON scraped_businesses(website);

-- User usage tracking: prevents abuse
CREATE TABLE IF NOT EXISTS user_usage (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    
    -- Current usage
    active_jobs INTEGER DEFAULT 0,
    total_jobs_today INTEGER DEFAULT 0,
    total_businesses_scraped_today INTEGER DEFAULT 0,
    
    -- Limits
    max_concurrent_jobs INTEGER DEFAULT 5,
    max_jobs_per_day INTEGER DEFAULT 50,
    max_businesses_per_day INTEGER DEFAULT 1000,
    
    -- Timestamps
    last_job_at TIMESTAMP WITH TIME ZONE,
    daily_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to reset daily usage
CREATE OR REPLACE FUNCTION reset_daily_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.daily_reset_at < NOW() - INTERVAL '1 day' THEN
        NEW.total_jobs_today := 0;
        NEW.total_businesses_scraped_today := 0;
        NEW.daily_reset_at := NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-reset daily usage
CREATE TRIGGER trigger_reset_daily_usage
    BEFORE UPDATE ON user_usage
    FOR EACH ROW
    EXECUTE FUNCTION reset_daily_usage();

-- Row Level Security (RLS) policies
ALTER TABLE scraping_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraped_businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_usage ENABLE ROW LEVEL SECURITY;

-- Users can only see their own jobs
CREATE POLICY "Users can view own jobs"
    ON scraping_jobs FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only see their own scraped businesses
CREATE POLICY "Users can view own businesses"
    ON scraped_businesses FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only see their own usage
CREATE POLICY "Users can view own usage"
    ON user_usage FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can do everything (for backend API)
CREATE POLICY "Service role full access jobs"
    ON scraping_jobs FOR ALL
    USING (true);

CREATE POLICY "Service role full access businesses"
    ON scraped_businesses FOR ALL
    USING (true);

CREATE POLICY "Service role full access usage"
    ON user_usage FOR ALL
    USING (true);
