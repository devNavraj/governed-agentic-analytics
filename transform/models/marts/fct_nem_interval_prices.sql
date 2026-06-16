-- Fact: one row per region per 5-minute settlement interval.
with stg as (
    select * from {{ ref('stg_aemo__nem_summary') }}
)

select
    nem_interval_key,
    region_id,
    settlement_date,
    settlement_day,
    settlement_hour,
    price_aud_mwh,
    total_demand_mw,
    net_interchange_mw,
    scheduled_generation_mw,
    semi_scheduled_generation_mw,
    price_status,
    is_administered_price,
    is_market_suspended,
    _ingested_at
from stg
