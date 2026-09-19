select
    last_updated,
    period_begin,
    period_end,
    region_id,
    region_type,
    region_name,
    homes_sold_nsa,
    median_sale_price_nsa_ as median_sale_price_nsa,
    median_sale_price_per_sqft_nsa_ as median_sale_price_per_sqft_nsa,
    median_new_listing_price_nsa_ as median_new_listing_price_nsa,
    active_listings_nsa,
    pending_sales_nsa

from {{ source('redfin_raw', 'metro_weekly_housing') }}