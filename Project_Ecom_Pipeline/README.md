# E-Commerce Data Pipeline (Medallion Architecture)

An automated 4-layer Medallion Data Pipeline using Python, Pandas, Data Quality Quarantining, and ADF pipeline orchestration layout.

## Data Processing Layers
- **Landing Layer (`data/landing`)**: Stores raw operational CSV files (`orders`, `order_items`, `customers`, `inventory`).
- **Bronze Layer (`data/bronze`)**: Raw layer appending ingestion metadata (`landing_timestamp`, `bronze_ingestion_timestamp`, `load_date`).
- **Silver Layer (`data/silver`)**: Cleans, deduplicates primary keys, enforces non-null checks, and routes invalid records into `orders_quarantine` and `order_items_quarantine`.
- **Gold Layer (`data/gold`)**: Aggregates key business KPIs (`daily_revenue`, `customer_ltv`) and generates automated data quality audit logs (`reconciliation_dq_summary`).