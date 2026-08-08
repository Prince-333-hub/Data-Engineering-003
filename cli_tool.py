import sqlite3

def generate_report():
    print("=== E-COMMERCE ORDER ANALYTICS SYSTEM ===")
    report_type = input("Enter report type (daily/weekly/monthly): ").strip().lower()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    conn = sqlite3.connect("analytics.db")
    cursor = conn.cursor()

    query = """
    SELECT 
        COUNT(DISTINCT o.order_id),
        COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0),
        COUNT(DISTINCT o.customer_id)
    FROM orders o
    JOIN order_items i ON o.order_id = i.order_id
    WHERE DATE(o.order_date) BETWEEN ? AND ?
    """
    cursor.execute(query, (start_date, end_date))
    total_orders, total_revenue, unique_customers = cursor.fetchone()

    top_products_query = """
    SELECT p.product_name, SUM(i.quantity) as total_qty
    FROM order_items i
    JOIN products p ON i.product_id = p.product_id
    JOIN orders o ON i.order_id = o.order_id
    WHERE DATE(o.order_date) BETWEEN ? AND ?
    GROUP BY p.product_name
    ORDER BY total_qty DESC
    LIMIT 3
    """
    cursor.execute(top_products_query, (start_date, end_date))
    top_products = cursor.fetchall()

    print("\n" + "="*30)
    print(f"REPORT SUMMARY ({report_type.upper()}) [{start_date} to {end_date}]")
    print("="*30)
    print(f"Total Orders:      {total_orders}")
    print(f"Total Revenue:     ${total_revenue:,.2f}")
    print(f"Unique Customers:  {unique_customers}")
    print("\nTop 3 Products Sold:")
    for name, qty in top_products:
        print(f" - {name}: {qty} units")
    print("="*30)

    conn.close()

if __name__ == "__main__":
    generate_report()