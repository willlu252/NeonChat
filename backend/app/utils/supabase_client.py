import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.client: Optional[Client] = None
        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        supabase_key = os.getenv("SUPABASE_KEY", "").strip()
        
        # Check if the values are placeholders or empty
        if (not supabase_url or not supabase_key or 
            supabase_url == "your_supabase_project_url" or 
            supabase_key == "your_supabase_anon_key"):
            print("WARNING: Supabase is not configured. Journal and metrics features will be disabled.")
            print("To enable these features, update SUPABASE_URL and SUPABASE_KEY in your .env file")
            self.client = None
        else:
            try:
                self.client = create_client(supabase_url, supabase_key)
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"WARNING: Failed to initialize Supabase client: {e}")
                self.client = None
    
    def get_client(self) -> Optional[Client]:
        return self.client
    
    def is_configured(self) -> bool:
        return self.client is not None

# Global instance - will be None if not configured
try:
    supabase_client = SupabaseClient()
except Exception as e:
    print(f"Failed to create Supabase client: {e}")
    supabase_client = None

# SQL Schema to run in Supabase SQL Editor
SUPABASE_SCHEMA = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal entries table
CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT,
    content TEXT NOT NULL,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    tags JSONB DEFAULT '[]'::jsonb,
    ai_observations TEXT,
    entry_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    word_count INTEGER DEFAULT 0
);

-- Daily metrics table
CREATE TABLE IF NOT EXISTS daily_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    sleep_hours DECIMAL(3,1),
    water_intake INTEGER,
    exercise_minutes INTEGER,
    steps INTEGER,
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    happiness_level INTEGER CHECK (happiness_level >= 1 AND happiness_level <= 10),
    meditation_minutes INTEGER,
    social_interaction_quality INTEGER CHECK (social_interaction_quality >= 1 AND social_interaction_quality <= 10),
    prayer_minutes INTEGER,
    gratitude_count INTEGER,
    work_satisfaction INTEGER CHECK (work_satisfaction >= 1 AND work_satisfaction <= 10),
    productivity_score INTEGER CHECK (productivity_score >= 1 AND productivity_score <= 10),
    wellbeing_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Chat transcripts table for journaling sessions
CREATE TABLE IF NOT EXISTS chat_transcripts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    session_duration INTEGER, -- in minutes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entries_entry_date ON journal_entries(entry_date);
CREATE INDEX idx_daily_metrics_user_id ON daily_metrics(user_id);
CREATE INDEX idx_daily_metrics_date ON daily_metrics(date);

-- Row Level Security (RLS) policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_transcripts ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Journal entries policies
CREATE POLICY "Users can view own journal entries" ON journal_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own journal entries" ON journal_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own journal entries" ON journal_entries
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own journal entries" ON journal_entries
    FOR DELETE USING (auth.uid() = user_id);

-- Daily metrics policies
CREATE POLICY "Users can view own metrics" ON daily_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own metrics" ON daily_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own metrics" ON daily_metrics
    FOR UPDATE USING (auth.uid() = user_id);

-- Chat transcripts policies
CREATE POLICY "Users can view own chat transcripts" ON chat_transcripts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own chat transcripts" ON chat_transcripts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Functions for triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate word count
CREATE OR REPLACE FUNCTION calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.word_count = array_length(string_to_array(NEW.content, ' '), 1);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for word count
CREATE TRIGGER calculate_journal_word_count BEFORE INSERT OR UPDATE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION calculate_word_count();
"""