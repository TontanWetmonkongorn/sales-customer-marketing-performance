SELECT channel, campaign_name, SUM(impressions) AS impressions, SUM(clicks) AS clicks,
       SUM(conversions) AS conversions, ROUND(SUM(spend), 2) AS spend,
       ROUND(SUM(revenue_generated), 2) AS reported_campaign_revenue,
       ROUND(100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 2) AS ctr_pct,
       ROUND(100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0), 2) AS click_conversion_pct,
       ROUND(1.0 * SUM(revenue_generated) / NULLIF(SUM(spend), 0), 3) AS recalculated_roas
FROM marketing_performance
GROUP BY channel, campaign_name
ORDER BY recalculated_roas DESC, channel, campaign_name;
