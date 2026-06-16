-- NEM region dimension, sourced from the nem_regions seed.
select
    region_id,
    region_name,
    state_territory,
    timezone
from {{ ref('nem_regions') }}
