
CREATE SCHEMA IF NOT EXISTS silver;

CREATE OR REPLACE TABLE silver.ga4_events AS
WITH typed AS (
    SELECT
        TRY_STRPTIME(
            NULLIF(TRIM(event_date), ''),
            '%Y%m%d'
        )::DATE AS event_date,

        MAKE_TIMESTAMP(
            TRY_CAST(event_timestamp AS BIGINT)
        ) AS event_timestamp,

        NULLIF(TRIM(event_name), '') AS event_name,
        NULLIF(TRIM(user_pseudo_id), '') AS user_pseudo_id,

        TRY_CAST(
            NULLIF(TRIM(ga_session_id), '')
            AS BIGINT
        ) AS ga_session_id,

        NULLIF(TRIM(first_user_source), '')
            AS first_user_source,

        NULLIF(TRIM(first_user_medium), '')
            AS first_user_medium,

        NULLIF(TRIM(first_user_campaign), '')
            AS first_user_campaign,

        NULLIF(TRIM(device_category), '')
            AS device_category,

        NULLIF(TRIM(country), '')
            AS country,

        TRY_CAST(
            NULLIF(TRIM(purchase_revenue), '')
            AS DOUBLE
        ) AS purchase_revenue

    FROM bronze.ga4_events
)

SELECT *
FROM typed
WHERE event_date IS NOT NULL
  AND event_timestamp IS NOT NULL
  AND event_name IS NOT NULL
  AND (purchase_revenue IS NULL OR purchase_revenue >= 0);
