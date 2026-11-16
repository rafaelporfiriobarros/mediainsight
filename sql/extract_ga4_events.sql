
SELECT
    event_date,
    event_timestamp,
    event_name,
    user_pseudo_id,

    (
        SELECT ep.value.int_value
        FROM UNNEST(event_params) AS ep
        WHERE ep.key = 'ga_session_id'
        LIMIT 1
    ) AS ga_session_id,

    traffic_source.source AS first_user_source,
    traffic_source.medium AS first_user_medium,
    traffic_source.name AS first_user_campaign,

    device.category AS device_category,
    geo.country AS country,

    ecommerce.purchase_revenue AS purchase_revenue

FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

WHERE
    _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'

ORDER BY
    event_date,
    event_timestamp;
