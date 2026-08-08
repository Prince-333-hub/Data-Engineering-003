import pandas as pd
import sqlite3
import re

# --- PART 2: DATA CLEANING ---
def clean_data():
    orders = pd.read_csv("orders.csv")
    products = pd.read_csv("products.csv")
    customers = pd.read_csv("customers.csv")
    items = pd.read_csv("order_items.csv")

    # 1. Clean Orders Date & handle NULL customer_id
    orders['order_date'] = pd.to_datetime(orders['order_date'], format='mixed', errors='coerce')
    orders['order_date'] = orders['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    orders['customer_id'] = orders['customer_id'].fillna("UNKNOWN")

    # 2. Clean Products
    products['product_name'] = products['product_name'].str.strip().str.title()

    # 3. Validate Emails
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_customers = customers[~customers['email'].astype(str).str.match(email_regex)]
    print(f"Invalid Emails Found: {len(invalid_customers)}")

    # 4. Check Referential Integrity
    orphan_items = items[~items['order_id'].isin(orders['order_id'])]
    print(f"Orphaned Order Items Found: {len(orphan_items)}")

    # Save cleaned CSVs
    orders.to_csv("cleaned_orders.csv", index=False)
    products.to_csv("cleaned_products.csv", index=False)
    customers.to_csv("cleaned_customers.csv", index=False)
    items.to_csv("cleaned_order_items.csv", index=False)
    print("Data cleaning completed and saved.")

# --- PART 3: SQL DATABASE SETUP & QUERIES ---
def run_sql_queries():
    conn = sqlite3.connect("analytics.db")
    
    # Load cleaned data into SQLite
    pd.read_csv("cleaned_orders.csv").to_sql("orders", conn, if_exists="replace", index=False)
    pd.read_csv("cleaned_products.csv").to_sql("products", conn, if_exists="replace", index=False)
    pd.read_csv("cleaned_customers.csv").to_sql("customers", conn, if_exists="replace", index=False)
    pd.read_csv("cleaned_order_items.csv").to_sql("order_items", conn, if_exists="replace", index=False)

    print("\n--- SQL Query 1: Total Revenue Per Category ---")
    q1 = """
    SELECT p.category, 
           SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS total_revenue
    FROM order_items i
    JOIN products p ON i.product_id = p.product_id
    WHERE i.quantity > 0
    GROUP BY p.category;
    """
    print(pd.read_sql_query(q1, conn))

    print("\n--- SQL Query 7: Running Totals ---")
    q7 = """
    SELECT o.region_code, o.order_date,
           SUM(i.quantity * i.unit_price * (1 - i.discount_percent/100.0)) AS daily_revenue,
           SUM(SUM(i.quantity * i.unit_price * (1 - i.discount_percent/100.0))) 
               OVER (PARTITION BY o.region_code ORDER BY o.order_date) AS running_total
    FROM orders o
    JOIN order_items i ON o.order_id = i.order_id
    GROUP BY o.region_code, o.order_date;
    """
    print(pd.read_sql_query(q7, conn).head())

    conn.close()

# --- PART 5: EDGE CASE TESTS ---
def test_edge_cases():
    items = pd.read_csv("cleaned_order_items.csv")
    orders = pd.read_csv("cleaned_orders.csv")

    assert (items['discount_percent'] > 100).sum() == 0, "Error: Invalid discount percentages present!"
    assert (items['quantity'] == 0).sum() == 0, "Error: Items with zero quantity present!"
    print("\nAll edge case assertion tests passed successfully!")

if __name__ == "__main__":
    clean_data()
    run_sql_queries()
    test_edge_cases()