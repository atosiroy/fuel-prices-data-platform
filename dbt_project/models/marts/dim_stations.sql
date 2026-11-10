select
    station_id,
    postal_code,
    left(postal_code, 2) as department,
    ville,
    adresse,
    latitude,
    longitude
from (
    select
        *,
        row_number() over (
            partition by station_id
            order by ingestion_date desc, price_updated_at desc
        ) as rn
    from {{ ref('stg_prices') }}
)
where rn = 1