select distinct
    fuel_id,
    fuel_name
from {{ ref('stg_prices') }}