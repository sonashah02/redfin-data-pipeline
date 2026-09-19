select
    stg.region_id,
    stg.region_name,
    stg.period_end,
    stg.median_sale_price_nsa,
    stg.median_sale_price_per_sqft_nsa,
    stg.median_new_listing_price_nsa,
    stg.homes_sold_nsa,
    stg.active_listings_nsa,
    stg.pending_sales_nsa,
    yoy.yoy_price_change_pct

from {{ ref('stg_redfin_metro_weekly') }} stg
left join {{ ref('int_redfin_yoy_price_change') }} yoy
    on stg.region_id = yoy.region_id
    and stg.period_end = yoy.period_end