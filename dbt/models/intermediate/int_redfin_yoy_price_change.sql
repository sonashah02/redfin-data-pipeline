with current_period as (
    select
        region_id,
        region_name,
        period_end,
        median_sale_price_nsa
    from {{ ref('stg_redfin_metro_weekly') }}
),

prior_year as (
    select
        region_id,
        period_end,
        median_sale_price_nsa as median_sale_price_nsa_prior_year
    from {{ ref('stg_redfin_metro_weekly') }}
)

select
    curr.region_id,
    curr.region_name,
    curr.period_end,
    curr.median_sale_price_nsa,
    prior.median_sale_price_nsa_prior_year,
    safe_divide(
        curr.median_sale_price_nsa - prior.median_sale_price_nsa_prior_year,
        prior.median_sale_price_nsa_prior_year
    ) as yoy_price_change_pct

from current_period curr
left join prior_year prior
    on curr.region_id = prior.region_id
    and prior.period_end = date_sub(curr.period_end, interval 52 week)