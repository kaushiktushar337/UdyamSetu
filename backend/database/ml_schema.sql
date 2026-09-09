-- UDYAMSETU ML & DECISION ENGINE DATABASE EXTENSION
-- PostgreSQL
-- ONLY NEW TABLES. Existing application/chatbot tables are excluded.

BEGIN;

-- 1. BUSINESS REFERENCE PROFILES
CREATE TABLE IF NOT EXISTS business_reference_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    minimum_capital NUMERIC(15,2),
    typical_project_cost NUMERIC(15,2),
    expected_monthly_revenue NUMERIC(15,2),
    expected_monthly_expenses NUMERIC(15,2),
    expected_profit_margin NUMERIC(7,2),
    typical_break_even_months NUMERIC(10,2),
    resource_requirements JSONB,
    infrastructure_requirements JSONB,
    risk_factors JSONB,
    data_source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_business_reference_profiles_category
ON business_reference_profiles(category);

-- 2. LOCATION BUSINESS METRICS
-- location_id should be linked to the existing locations table.
CREATE TABLE IF NOT EXISTS location_business_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL,
    business_category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    demand_score NUMERIC(5,2) CHECK (demand_score BETWEEN 0 AND 100),
    competition_count INTEGER CHECK (competition_count >= 0),
    competition_score NUMERIC(5,2) CHECK (competition_score BETWEEN 0 AND 100),
    average_market_price NUMERIC(15,2),
    opportunity_score NUMERIC(5,2) CHECK (opportunity_score BETWEEN 0 AND 100),
    data_source TEXT,
    data_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_location_business_metrics_location_category
ON location_business_metrics(location_id, business_category);

-- 3. BUSINESS ANALYSES
-- user_id, business_id and location_id should be connected to existing tables.
CREATE TABLE IF NOT EXISTS business_analyses (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    business_id UUID NOT NULL,
    location_id UUID NOT NULL,
    overall_score NUMERIC(5,2) CHECK (overall_score BETWEEN 0 AND 100),
    decision VARCHAR(30) NOT NULL,
    confidence NUMERIC(5,4) CHECK (confidence BETWEEN 0 AND 1),
    analysis_status VARCHAR(30) NOT NULL DEFAULT 'completed',
    engine_version VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_business_analyses_user
ON business_analyses(user_id);

CREATE INDEX IF NOT EXISTS idx_business_analyses_business
ON business_analyses(business_id);

-- 4. ANALYSIS SCORES
CREATE TABLE IF NOT EXISTS analysis_scores (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE,
    market_score NUMERIC(5,2) CHECK (market_score BETWEEN 0 AND 100),
    operational_score NUMERIC(5,2) CHECK (operational_score BETWEEN 0 AND 100),
    financial_score NUMERIC(5,2) CHECK (financial_score BETWEEN 0 AND 100),
    risk_score NUMERIC(5,2) CHECK (risk_score BETWEEN 0 AND 100),
    overall_score NUMERIC(5,2) CHECK (overall_score BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

-- 5. MARKET ANALYSES
CREATE TABLE IF NOT EXISTS market_analyses (
    market_analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE,
    demand_score NUMERIC(5,2) CHECK (demand_score BETWEEN 0 AND 100),
    competition_score NUMERIC(5,2) CHECK (competition_score BETWEEN 0 AND 100),
    market_gap_score NUMERIC(5,2) CHECK (market_gap_score BETWEEN 0 AND 100),
    pricing_score NUMERIC(5,2) CHECK (pricing_score BETWEEN 0 AND 100),
    opportunity_score NUMERIC(5,2) CHECK (opportunity_score BETWEEN 0 AND 100),
    demand_level VARCHAR(20),
    competition_level VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

-- 6. OPERATIONAL ANALYSES
CREATE TABLE IF NOT EXISTS operational_analyses (
    operational_analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE,
    resource_score NUMERIC(5,2) CHECK (resource_score BETWEEN 0 AND 100),
    infrastructure_score NUMERIC(5,2) CHECK (infrastructure_score BETWEEN 0 AND 100),
    supply_chain_score NUMERIC(5,2) CHECK (supply_chain_score BETWEEN 0 AND 100),
    logistics_score NUMERIC(5,2) CHECK (logistics_score BETWEEN 0 AND 100),
    operational_score NUMERIC(5,2) CHECK (operational_score BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

-- 7. FINANCIAL ANALYSES
CREATE TABLE IF NOT EXISTS financial_analyses (
    financial_analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE,
    estimated_project_cost NUMERIC(15,2),
    available_capital NUMERIC(15,2),
    funding_gap NUMERIC(15,2),
    estimated_monthly_revenue NUMERIC(15,2),
    estimated_monthly_expenses NUMERIC(15,2),
    estimated_monthly_profit NUMERIC(15,2),
    break_even_months NUMERIC(10,2),
    loan_amount NUMERIC(15,2),
    estimated_emi NUMERIC(15,2),
    repayment_feasibility VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

-- 8. ANALYSIS RISKS
CREATE TABLE IF NOT EXISTS analysis_risks (
    risk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    risk_type VARCHAR(50) NOT NULL,
    risk_score NUMERIC(5,2) CHECK (risk_score BETWEEN 0 AND 100),
    severity VARCHAR(20),
    description TEXT,
    mitigation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analysis_risks_analysis
ON analysis_risks(analysis_id);

-- 9. ANALYSIS RECOMMENDATIONS
CREATE TABLE IF NOT EXISTS analysis_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    category VARCHAR(50),
    priority VARCHAR(20),
    recommendation TEXT NOT NULL,
    expected_impact TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES business_analyses(analysis_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analysis_recommendations_analysis
ON analysis_recommendations(analysis_id);

COMMIT;

-- END OF UDYAMSETU ML & DECISION ENGINE DATABASE EXTENSION
