-- keeps one row per station, fuel and price timestamp
select
    md5(station_id || '-' || fuel_id || '-' || cast(price_updated_at as varchar)) as price_key,
    station_id,
    fuel_id,
    price_updated_at,
    price_eur,
    ingestion_date
from {{ ref('stg_prices') }}
qualify row_number() over (
    partition by station_id, fuel_id, price_updated_at
    order by ingestion_date
) = 1
