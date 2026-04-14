-- ============================================================
-- Berlin Housing Affordability Project
-- Step 3: Analysis Queries
-- ============================================================
-- This file contains the main SQL queries used to explore
-- Berlin housing prices, district differences, and links
-- to income and social structure indicators.
-- ============================================================

-- ============================================================
-- 1. HOUSING OVERVIEW
-- ============================================================

-- Total number of housing listings
SELECT COUNT(*) AS total_listings
FROM raw_housing_listings;

-- Average, median-like overview using aggregates
SELECT
    ROUND(AVG(base_rent), 2) AS avg_base_rent,
    ROUND(AVG(total_rent), 2) AS avg_total_rent,
    ROUND(AVG(living_space), 2) AS avg_living_space,
    ROUND(AVG(no_rooms), 2) AS avg_rooms,
    ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
FROM raw_housing_listings;

-- Missing values overview for selected key columns
SELECT
    COUNT(*) FILTER (WHERE total_rent IS NULL) AS missing_total_rent,
    COUNT(*) FILTER (WHERE floor IS NULL) AS missing_floor,
    COUNT(*) FILTER (WHERE number_of_floors IS NULL) AS missing_number_of_floors,
    COUNT(*) FILTER (WHERE year_constructed IS NULL) AS missing_year_constructed,
    COUNT(*) FILTER (WHERE condition IS NULL) AS missing_condition,
    COUNT(*) FILTER (WHERE interior_qual IS NULL) AS missing_interior_qual
FROM raw_housing_listings;


-- ============================================================
-- 2. DISTRICT COMPARISON
-- ============================================================

-- Average rent per sqm by Bezirk
SELECT
    bezirk,
    COUNT(*) AS listing_count,
    ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm,
    ROUND(AVG(base_rent), 2) AS avg_base_rent,
    ROUND(AVG(living_space), 2) AS avg_living_space,
    ROUND(AVG(no_rooms), 2) AS avg_rooms
FROM raw_housing_listings
GROUP BY bezirk
ORDER BY avg_rent_per_sqm DESC;

-- Top 10 most expensive neighborhoods by average rent per sqm
SELECT
    neighborhood,
    COUNT(*) AS listing_count,
    ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
FROM raw_housing_listings
GROUP BY neighborhood
HAVING COUNT(*) >= 20
ORDER BY avg_rent_per_sqm DESC
LIMIT 10;

-- Bottom 10 least expensive neighborhoods by average rent per sqm
SELECT
    neighborhood,
    COUNT(*) AS listing_count,
    ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
FROM raw_housing_listings
GROUP BY neighborhood
HAVING COUNT(*) >= 20
ORDER BY avg_rent_per_sqm ASC
LIMIT 10;

-- Average rent per sqm by district part
SELECT
    district_part,
    ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
FROM raw_housing_listings
GROUP BY district_part
ORDER BY avg_rent_per_sqm DESC;


-- ============================================================
-- 3. AFFORDABILITY + SOCIAL COMPARISON
-- ============================================================

-- Housing summary by Bezirk
WITH housing_bezirk AS (
    SELECT
        bezirk,
        COUNT(*) AS listing_count,
        ROUND(AVG(base_rent), 2) AS avg_base_rent,
        ROUND(AVG(total_rent), 2) AS avg_total_rent,
        ROUND(AVG(living_space), 2) AS avg_living_space,
        ROUND(AVG(no_rooms), 2) AS avg_rooms,
        ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rent_per_sqm)::numeric, 2) AS median_rent_per_sqm
    FROM raw_housing_listings
    GROUP BY bezirk
)

SELECT *
FROM housing_bezirk
ORDER BY avg_rent_per_sqm DESC;

-- Merge housing + income
WITH housing_bezirk AS (
    SELECT
        bezirk,
        COUNT(*) AS listing_count,
        ROUND(AVG(base_rent), 2) AS avg_base_rent,
        ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rent_per_sqm)::numeric, 2) AS median_rent_per_sqm
    FROM raw_housing_listings
    GROUP BY bezirk
)
SELECT
    h.bezirk,
    h.listing_count,
    h.avg_rent_per_sqm,
    h.avg_base_rent,
    i.avg_monthly_income_eur,
    i.median_monthly_income_eur,
    ROUND((h.avg_base_rent / i.avg_monthly_income_eur) * 100, 1) AS rent_burden_pct,
    ROUND((h.median_rent_per_sqm * 60 / i.median_monthly_income_eur) * 100, 1) AS median_rent_burden_pct
FROM housing_bezirk h
LEFT JOIN raw_income_by_district i
    ON h.bezirk = i.district_name
ORDER BY rent_burden_pct DESC;

-- Merge housing + social atlas
WITH housing_bezirk AS (
    SELECT
        bezirk,
        COUNT(*) AS listing_count,
        ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
    FROM raw_housing_listings
    GROUP BY bezirk
)
SELECT
    h.bezirk,
    h.listing_count,
    h.avg_rent_per_sqm,
    s.gesix_2022,
    s.esix_2022,
    s.di_2022,
    s.dii_2022,
    s.diii_2022
FROM housing_bezirk h
LEFT JOIN raw_social_atlas s
    ON h.bezirk = s.district_name
ORDER BY h.avg_rent_per_sqm DESC;

-- Full comparison: housing + income + social
WITH housing_bezirk AS (
    SELECT
        bezirk,
        COUNT(*) AS listing_count,
        ROUND(AVG(base_rent), 2) AS avg_base_rent,
        ROUND(AVG(rent_per_sqm), 2) AS avg_rent_per_sqm
    FROM raw_housing_listings
    GROUP BY bezirk
)
SELECT
    h.bezirk,
    h.listing_count,
    h.avg_rent_per_sqm,
    h.avg_base_rent,
    i.avg_monthly_income_eur,
    i.unemployment_rate_pct,
    i.transfer_income_share_pct,
    i.population,
    s.gesix_2022,
    s.esix_2022,
    ROUND((h.avg_base_rent / i.avg_monthly_income_eur) * 100, 1) AS rent_burden_pct
FROM housing_bezirk h
LEFT JOIN raw_income_by_district i
    ON h.bezirk = i.district_name
LEFT JOIN raw_social_atlas s
    ON h.bezirk = s.district_name
ORDER BY rent_burden_pct DESC;


-- ============================================================
-- END OF ANALYSIS QUERIES
-- ============================================================