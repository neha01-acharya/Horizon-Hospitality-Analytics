
SEASONAL_KPI_QUERY = """
SELECT *
FROM agg_seasonal_kpis
ORDER BY year, season, hotel_name
"""
