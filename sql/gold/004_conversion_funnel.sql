
-- ============================================================
-- MEDIAINSIGHT 360 - ETAPA 4
-- FUNIL DESCRITIVO DE EVENTOS GA4
--
-- Grao: data + etapa do funil
-- Nao representa progressao sequencial de usuarios.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.conversion_funnel AS

WITH funnel_steps AS (
    SELECT
        1 AS step_order,
        'view_item' AS event_name,
        'Visualizacao de produto' AS step_name

    UNION ALL SELECT
        2, 'add_to_cart', 'Adicao ao carrinho'

    UNION ALL SELECT
        3, 'begin_checkout', 'Inicio do checkout'

    UNION ALL SELECT
        4, 'add_payment_info', 'Informacoes de pagamento'

    UNION ALL SELECT
        5, 'purchase', 'Compra'
),

event_dates AS (
    SELECT DISTINCT event_date
    FROM silver.ga4_events
),

event_metrics AS (
    SELECT
        event_date,
        event_name,
        COUNT(*) AS total_events,
        COUNT(DISTINCT user_pseudo_id) AS unique_users,

        COUNT(DISTINCT (
            user_pseudo_id,
            ga_session_id
        )) FILTER (
            WHERE user_pseudo_id IS NOT NULL
              AND ga_session_id IS NOT NULL
        ) AS distinct_sessions

    FROM silver.ga4_events

    WHERE event_name IN (
        'view_item',
        'add_to_cart',
        'begin_checkout',
        'add_payment_info',
        'purchase'
    )

    GROUP BY event_date, event_name
)

SELECT
    d.event_date,
    s.step_order,
    s.event_name,
    s.step_name,

    COALESCE(m.total_events, 0)
        AS total_events,

    COALESCE(m.unique_users, 0)
        AS unique_users,

    COALESCE(m.distinct_sessions, 0)
        AS distinct_sessions

FROM event_dates AS d

CROSS JOIN funnel_steps AS s

LEFT JOIN event_metrics AS m
    ON d.event_date = m.event_date
   AND s.event_name = m.event_name;
