select
    s.department,
    ft.fuel_id,
    ft.fuel_name,
    date_trunc('week', f.price_updated_at) as week_start,
    round(avg(f.price_eur), 3) as avg_price_eur,
    count(*) as price_points
from {{ ref('fact_prices') }} as f
join {{ ref('dim_stations') }} as s on f.station_id = s.station_id
join {{ ref('dim_fuel_type') }} as ft on f.fuel_id = ft.fuel_id
group by 1, 2, 3, 4