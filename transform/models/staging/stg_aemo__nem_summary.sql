-- Cleaned, de-duplicated AEMO NEM summary: one row per region per 5-min interval.
with source as (
    select * from {{ source('raw', 'aemo__nem_summary') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by REGIONID, SETTLEMENTDATE
            order by _ingested_at desc
        ) as _row_num
    from source
),

renamed as (
    select
        to_hex(md5(concat(REGIONID, '|', cast(SETTLEMENTDATE as string)))) as nem_interval_key,
        REGIONID                                      as region_id,
        SETTLEMENTDATE                                as settlement_date,
        date(SETTLEMENTDATE)                          as settlement_day,
        extract(hour from SETTLEMENTDATE)             as settlement_hour,
        cast(PRICE as numeric)                        as price_aud_mwh,
        cast(TOTALDEMAND as numeric)                  as total_demand_mw,
        cast(NETINTERCHANGE as numeric)               as net_interchange_mw,
        cast(SCHEDULEDGENERATION as numeric)          as scheduled_generation_mw,
        cast(SEMISCHEDULEDGENERATION as numeric)      as semi_scheduled_generation_mw,
        PRICE_STATUS                                  as price_status,
        coalesce(APCFLAG, 0) = 1                      as is_administered_price,
        coalesce(MARKETSUSPENDEDFLAG, 0) = 1          as is_market_suspended,
        INTERCONNECTORFLOWS                           as interconnector_flows_raw,
        _source,
        _batch_id,
        _ingested_at
    from deduplicated
    where _row_num = 1
)

select * from renamed
