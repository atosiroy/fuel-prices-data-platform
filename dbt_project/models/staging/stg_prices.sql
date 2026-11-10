select
    station_id,
    cp as postal_code,
    pop,
    adresse,
    ville,
    latitude,
    longitude,
    automate_24_24,
    services,
    fuel_id,
    fuel_name,
    maj as price_updated_at,
    price_eur,
    ingestion_date
from read_parquet('data/silver/prices/*/*.parquet', hive_partitioning = false)