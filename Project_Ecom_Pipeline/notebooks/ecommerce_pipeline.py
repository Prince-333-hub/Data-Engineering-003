import os
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANDING_DIR = os.path.join(BASE_DIR, "data", "landing")
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

# 1. LANDING TO BRONZE
tables = ["orders", "order_items", "customers", "inventory"]

for table in tables:
    csv_path = os.path.join(LANDING_DIR, f"{table}.csv")
    df = pd.read_csv(csv_path, dtype=str)
    
    df["landing_timestamp"] = datetime.now().isoformat()
    df["bronze_ingestion_timestamp"] = datetime.now().isoformat()
    df["load_date"] = datetime.now().strftime("%Y-%m-%d")
    
    df.to_csv(os.path.join(BRONZE_DIR, f"{table}.csv"), index=False)

# 2. BRONZE TO SILVER
# Orders Processing
df_orders = pd.read_csv(os.path.join(BRONZE_DIR, "orders.csv"))
order_pk = "order_id" if "order_id" in df_orders.columns else ("id" if "id" in df_orders.columns else None)
if order_pk:
    df_orders = df_orders.sort_values("bronze_ingestion_timestamp").drop_duplicates(subset=[order_pk], keep="last")

df_orders["total_amount"] = pd.to_numeric(df_orders["total_amount"], errors="coerce")
valid_status = ["placed", "shipped", "delivered", "cancelled"]

cond_valid_orders = (
    df_orders["status"].str.lower().isin(valid_status) &
    (df_orders["total_amount"] > 0) &
    df_orders["customer_id"].notnull()
)

df_orders_clean = df_orders[cond_valid_orders].copy()
df_orders_quarantine = df_orders[~cond_valid_orders].copy()
df_orders_quarantine["quarantine_reason"] = "Invalid status, amount, or null customer_id"

df_orders_clean.to_csv(os.path.join(SILVER_DIR, "orders.csv"), index=False)
df_orders_quarantine.to_csv(os.path.join(SILVER_DIR, "orders_quarantine.csv"), index=False)

# Order Items Processing
df_items = pd.read_csv(os.path.join(BRONZE_DIR, "order_items.csv"))

item_pk = None
for candidate in ["order_item_id", "id", "item_id"]:
    if candidate in df_items.columns:
        item_pk = candidate
        break

if item_pk:
    df_items = df_items.sort_values("bronze_ingestion_timestamp").drop_duplicates(subset=[item_pk], keep="last")
elif "order_id" in df_items.columns and "product_id" in df_items.columns:
    df_items = df_items.sort_values("bronze_ingestion_timestamp").drop_duplicates(subset=["order_id", "product_id"], keep="last")
else:
    df_items = df_items.sort_values("bronze_ingestion_timestamp").drop_duplicates(keep="last")

df_items["quantity"] = pd.to_numeric(df_items["quantity"], errors="coerce")
df_items["unit_price"] = pd.to_numeric(df_items["unit_price"], errors="coerce")

cond_valid_items = (df_items["quantity"] > 0) & (df_items["unit_price"] > 0)

df_items_clean = df_items[cond_valid_items].copy()
df_items_quarantine = df_items[~cond_valid_items].copy()
df_items_quarantine["quarantine_reason"] = "Invalid quantity or price"

df_items_clean.to_csv(os.path.join(SILVER_DIR, "order_items.csv"), index=False)
df_items_quarantine.to_csv(os.path.join(SILVER_DIR, "order_items_quarantine.csv"), index=False)

# Inventory Processing
df_inv = pd.read_csv(os.path.join(BRONZE_DIR, "inventory.csv"))
stock_col = "stock_quantity" if "stock_quantity" in df_inv.columns else ("quantity" if "quantity" in df_inv.columns else None)
if stock_col:
    df_inv = df_inv.dropna(subset=[stock_col])
df_inv.to_csv(os.path.join(SILVER_DIR, "inventory.csv"), index=False)

# Customers Processing
df_cust = pd.read_csv(os.path.join(BRONZE_DIR, "customers.csv"))
cust_pk = "customer_id" if "customer_id" in df_cust.columns else ("id" if "id" in df_cust.columns else None)
if cust_pk:
    df_cust = df_cust.drop_duplicates(subset=[cust_pk], keep="last")
df_cust.to_csv(os.path.join(SILVER_DIR, "customers.csv"), index=False)

# 3. SILVER TO GOLD
df_silver_orders = pd.read_csv(os.path.join(SILVER_DIR, "orders.csv"))
df_silver_orders["order_date"] = pd.to_datetime(df_silver_orders["order_date"], errors="coerce")
df_silver_orders["order_date_only"] = df_silver_orders["order_date"].dt.date

daily_rev = df_silver_orders.groupby("order_date_only").agg(
    total_revenue=("total_amount", "sum"),
    order_count=("order_id", "count"),
    avg_order_value=("total_amount", "mean")
).reset_index()
daily_rev.to_csv(os.path.join(GOLD_DIR, "daily_revenue.csv"), index=False)

cust_ltv = df_silver_orders.groupby("customer_id").agg(
    lifetime_spend=("total_amount", "sum"),
    order_frequency=("order_id", "count")
).reset_index()

def assign_segment(spend):
    if spend > 5000: return "VIP"
    if spend > 2000: return "High Value"
    if spend > 500: return "Mid Value"
    return "Low Value"

cust_ltv["segment"] = cust_ltv["lifetime_spend"].apply(assign_segment)
cust_ltv.to_csv(os.path.join(GOLD_DIR, "customer_ltv.csv"), index=False)

# 4. RECONCILIATION
b_count = len(df_orders)
s_count = len(df_orders_clean)
q_count = len(df_orders_quarantine)

dq_summary = pd.DataFrame([{
    "bronze_row_count": b_count,
    "silver_row_count": s_count,
    "quarantined_rows": q_count,
    "pass_rate_pct": round((s_count / b_count) * 100, 2) if b_count > 0 else 0,
    "quarantine_rate_pct": round((q_count / b_count) * 100, 2) if b_count > 0 else 0
}])
dq_summary.to_csv(os.path.join(GOLD_DIR, "reconciliation_dq_summary.csv"), index=False)

print("Pipeline executed successfully! All Medallion layers populated.")