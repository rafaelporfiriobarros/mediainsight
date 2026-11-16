
-- ============================================================
-- MEDIAINSIGHT 360
-- ETAPA 4 - CAMADA GOLD
-- TABELA: gold.marketing_daily
-- ============================================================
--
-- Grao: uma linha por data de evento.
--
-- Origem: silver.ga4_events
-- Destino: gold.marketing_daily
--
-- ============================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.marketing_daily AS

WITH events AS (

    SELECT
        event_date,
        event_name,
        user_pseudo_id,
        ga_session_id,
        purchase_revenue,

        -- Chave composta da sessao.
        -- Evita contar somente o ga_session_id,
        -- que nao e globalmente unico.
        CASE
            WHEN user_pseudo_id IS NOT NULL
             AND ga_session_id IS NOT NULL
            THEN
                user_pseudo_id
                || ':'
                || CAST(ga_session_id AS VARCHAR)
            ELSE NULL
        END AS session_key

    FROM silver.ga4_events

),

daily_metrics AS (

    SELECT
        event_date,

        COUNT(*) AS total_events,

        COUNT(DISTINCT user_pseudo_id)
            AS unique_users,

        COUNT(DISTINCT session_key)
            AS total_sessions,

        COUNT(*) FILTER (
            WHERE event_name = 'page_view'
        ) AS page_views,

        COUNT(*) FILTER (
            WHERE event_name = 'user_engagement'
        ) AS engagement_events,

        COUNT(*) FILTER (
            WHERE event_name = 'purchase'
        ) AS purchases,

        COUNT(DISTINCT session_key) FILTER (
            WHERE event_name = 'purchase'
        ) AS purchasing_sessions,

        COALESCE(
            SUM(purchase_revenue),
            0
        ) AS total_revenue

    FROM events

    GROUP BY event_date

)

SELECT
    event_date,
    total_events,
    unique_users,
    total_sessions,
    page_views,
    engagement_events,
    purchases,
    purchasing_sessions,
    total_revenue,

    CASE
        WHEN total_sessions > 0
        THEN
            purchasing_sessions * 1.0
            / total_sessions
        ELSE NULL
    END AS session_conversion_rate,

    CASE
        WHEN total_sessions > 0
        THEN
            total_revenue
            / total_sessions
        ELSE NULL
    END AS revenue_per_session

FROM daily_metrics;
