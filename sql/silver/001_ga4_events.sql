
-- ============================================================
-- MEDIAINSIGHT 360
-- ETAPA 3 - TRANSFORMACAO E QUALIDADE DE DADOS
-- CAMADA SILVER - EVENTOS GA4
-- ============================================================
--
-- Origem: bronze.ga4_events
-- Destino: silver.ga4_events
--
-- Objetivos:
-- 1. Padronizar os tipos de dados.
-- 2. Tratar strings vazias e valores nulos.
-- 3. Validar datas, timestamps e nomes de eventos.
-- 4. Rejeitar receitas negativas.
-- 5. Preservar os dados originais na Bronze.
-- 6. Permitir reexecucao idempotente.
--
-- ============================================================


-- 1. CRIACAO DO SCHEMA SILVER

CREATE SCHEMA IF NOT EXISTS silver;


-- 2. TRANSFORMACAO DOS EVENTOS GA4

CREATE OR REPLACE TABLE silver.ga4_events AS

WITH typed AS (

    SELECT

        -- Data do evento: YYYYMMDD -> DATE
        TRY_STRPTIME(
            NULLIF(TRIM(event_date), ''),
            '%Y%m%d'
        )::DATE AS event_date,

        -- Timestamp GA4:
        -- Unix em microssegundos -> TIMESTAMP UTC
        MAKE_TIMESTAMP(
            TRY_CAST(
                NULLIF(TRIM(event_timestamp), '')
                AS BIGINT
            )
        ) AS event_timestamp,

        -- Nome do evento
        NULLIF(
            TRIM(event_name),
            ''
        ) AS event_name,

        -- Identificador pseudonimo do usuario
        NULLIF(
            TRIM(user_pseudo_id),
            ''
        ) AS user_pseudo_id,

        -- Identificador numerico da sessao
        TRY_CAST(
            NULLIF(TRIM(ga_session_id), '')
            AS BIGINT
        ) AS ga_session_id,

        -- Origem da primeira aquisicao do usuario
        NULLIF(
            TRIM(first_user_source),
            ''
        ) AS first_user_source,

        -- Midia da primeira aquisicao do usuario
        NULLIF(
            TRIM(first_user_medium),
            ''
        ) AS first_user_medium,

        -- Campanha da primeira aquisicao do usuario
        NULLIF(
            TRIM(first_user_campaign),
            ''
        ) AS first_user_campaign,

        -- Categoria do dispositivo
        NULLIF(
            TRIM(device_category),
            ''
        ) AS device_category,

        -- Pais do evento
        NULLIF(
            TRIM(country),
            ''
        ) AS country,

        -- Receita da compra
        TRY_CAST(
            NULLIF(TRIM(purchase_revenue), '')
            AS DOUBLE
        ) AS purchase_revenue

    FROM bronze.ga4_events

),

validated AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,
        ga_session_id,
        first_user_source,
        first_user_medium,
        first_user_campaign,
        device_category,
        country,
        purchase_revenue

    FROM typed

    WHERE
        -- Data obrigatoria e valida
        event_date IS NOT NULL

        -- Timestamp obrigatorio e valido
        AND event_timestamp IS NOT NULL

        -- Nome do evento obrigatorio
        AND event_name IS NOT NULL

        -- Receita pode ser nula, mas nao negativa
        AND (
            purchase_revenue IS NULL
            OR purchase_revenue >= 0
        )

)

SELECT
    event_date,
    event_timestamp,
    event_name,
    user_pseudo_id,
    ga_session_id,
    first_user_source,
    first_user_medium,
    first_user_campaign,
    device_category,
    country,
    purchase_revenue

FROM validated;
