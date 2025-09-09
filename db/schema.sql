-- schema.sql
-- Place your PostgreSQL DDL statements here for the star schema.

CREATE TABLE IF NOT EXISTS fact_requests (
    id TEXT PRIMARY KEY,
    status TEXT,
    request_type TEXT,
    description TEXT,
    created TIMESTAMP,
    last_updated TIMESTAMP,
    reporter_display TEXT,
    location_detail TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location TEXT,
    commission_district TEXT,
    computed_region_9cfm_spy5 TEXT,
    computed_region_43jd_v64e TEXT,
    computed_region_axii_i744 TEXT,
    computed_region_ndi2_bfht TEXT,
    computed_region_u9vc_vmbc TEXT,
    computed_region_4rat_gsiv TEXT,
    computed_region_qsqf_gz5q TEXT,
    closed TIMESTAMP,
    minutes_to_close DOUBLE PRECISION,
    days_to_close DOUBLE PRECISION,
    police_sector TEXT,
    acknowledged TIMESTAMP,
    minutes_to_acknowledge DOUBLE PRECISION,
    assigned_to TEXT,
    reopened BOOLEAN
);
