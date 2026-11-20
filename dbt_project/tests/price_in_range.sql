select *
from {{ ref('fact_prices') }}
where price_eur <= 0 or price_eur >= 5