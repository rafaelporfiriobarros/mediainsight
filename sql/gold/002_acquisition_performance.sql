
CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.acquisition_performance AS

WITH events AS (
    SELECT
        event_date,
        COALESCE(first_user_source, '(not set)')
            AS first_user_source,
        COALESCE(first_user_medium, '(not set)')
            AS first_user_medium,
        event_name,
        user_pseudo_id,
        purchase_revenue,

        CASE
            WHEN user_pseudo_id IS NOT NULL
             AND ga_session_id IS NOT NULL
            THEN user_pseudo_id || ':' ||
                 CAST(ga_session_id AS VARCHAR)
            ELSE NULL
        END AS session_key

    FROM silver.ga4_events
)

SELECT
    event_date,
    first_user_source,
    first_user_medium,

    COUNT(*) AS total_events,

    COUNT(DISTINCT user_pseudo_id)
        AS unique_users,

    COUNT(DISTINCT session_key)
        AS total_sessions,

    COUNT(*) FILTER (
        WHERE event_name = 'page_view'
    ) AS page_views,

    COUNT(*) FILTER (
        WHERE event_name = 'purchase'
    ) AS purchases,

    COUNT(DISTINCT session_key) FILTER (
        WHERE event_name = 'purchase'
    ) AS purchasing_sessions,

    COALESCE(SUM(purchase_revenue), 0)
        AS total_revenue

FROM events

GROUP BY
    event_date,
    first_user_source,
    first_user_medium;
