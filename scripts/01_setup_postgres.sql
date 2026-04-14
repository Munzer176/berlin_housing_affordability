-- ============================================================
-- Berlin Housing Affordability Project
-- Step 1: PostgreSQL Database Setup
-- ============================================================
-- This file creates the raw tables used in the project.
--
-- IMPORTANT:
-- Create the database first, then connect to it before running this file.
--
-- Example:
--   createdb berlin_housing
--   psql -d berlin_housing -f scripts/01_setup_postgres.sql
-- ============================================================

-- ============================================================
-- RAW TABLES (source data loaded from CSVs)
-- ============================================================

-- Raw housing listings from Berlin housing dataset
CREATE TABLE IF NOT EXISTS raw_housing_listings (
    id SERIAL PRIMARY KEY,
    regio1 VARCHAR(50),
    regio2 VARCHAR(50),
    regio3 VARCHAR(100),
    base_rent NUMERIC(10,2),
    total_rent NUMERIC(10,2),
    living_space NUMERIC(10,2),
    no_rooms NUMERIC(4,1),
    floor NUMERIC(4,0),
    number_of_floors NUMERIC(4,0),
    year_constructed INTEGER,
    condition VARCHAR(50),
    interior_qual VARCHAR(50),
    lift BOOLEAN,
    balcony BOOLEAN,
    has_kitchen BOOLEAN,
    cellar BOOLEAN,
    garden BOOLEAN,
    type_of_flat VARCHAR(50),
    service_charge NUMERIC(10,2),
    heating_type VARCHAR(50),
    newly_const BOOLEAN,
    picture_count INTEGER,
    price_trend NUMERIC(6,2),
    date_period VARCHAR(10),
    rent_per_sqm NUMERIC(8,4),
    neighborhood VARCHAR(100),
    district_part VARCHAR(100),
    bezirk VARCHAR(100)
);

-- Raw income data by district
CREATE TABLE IF NOT EXISTS raw_income_by_district (
    id SERIAL PRIMARY KEY,
    district_name VARCHAR(100),
    avg_monthly_income_eur NUMERIC(10,2),
    median_monthly_income_eur NUMERIC(10,2),
    unemployment_rate_pct NUMERIC(5,2),
    population INTEGER,
    transfer_income_share_pct NUMERIC(5,2)
);

-- Raw social atlas data by district
CREATE TABLE IF NOT EXISTS raw_social_atlas (
    id SERIAL PRIMARY KEY,
    district_id INTEGER,
    district_name VARCHAR(100),
    gesix_2013 NUMERIC(12,8),
    gesix_2022 NUMERIC(12,8),
    esix_2013 NUMERIC(12,8),
    esix_2022 NUMERIC(12,8),
    di_2013 NUMERIC(12,8),
    di_2022 NUMERIC(12,8),
    dii_2013 NUMERIC(12,8),
    dii_2022 NUMERIC(12,8),
    diii_2013 NUMERIC(12,8),
    diii_2022 NUMERIC(12,8)
);

-- Supporting reference table: summarized rent and buy prices
CREATE TABLE IF NOT EXISTS raw_rent_prices (
    id SERIAL PRIMARY KEY,
    borough_name VARCHAR(100),
    district_name VARCHAR(100),
    rent_min_eur_sqm NUMERIC(8,2),
    rent_avg_eur_sqm NUMERIC(8,2),
    rent_max_eur_sqm NUMERIC(8,2),
    buy_min_eur_sqm NUMERIC(10,2),
    buy_avg_eur_sqm NUMERIC(10,2),
    buy_max_eur_sqm NUMERIC(10,2),
    source_url TEXT
);

-- ============================================================
-- INDEXES for performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_housing_bezirk
    ON raw_housing_listings(bezirk);

CREATE INDEX IF NOT EXISTS idx_housing_rent
    ON raw_housing_listings(rent_per_sqm);

CREATE INDEX IF NOT EXISTS idx_income_district
    ON raw_income_by_district(district_name);

CREATE INDEX IF NOT EXISTS idx_social_district
    ON raw_social_atlas(district_name);

CREATE INDEX IF NOT EXISTS idx_rent_prices_district
    ON raw_rent_prices(district_name);

-- ============================================================
-- VERIFY
-- ============================================================

SELECT 'Raw tables created successfully.' AS status;