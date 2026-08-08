import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)

# 1. Customers CSV
customer_ids = [f"CUST_{i:04d}" for i in range(1, 201)]
customers = []
for cid in customer_ids:
    email = fake.email()
    # 2% invalid emails
    if random.random() < 0.02:
        email = email.replace("@", "")
    
    customers.append({
        "customer_id": cid,
        "customer_name": fake.name(),
        "email": email,
        "registration_date": fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d"),
        "customer_type": random.choice(["REGULAR", "PREMIUM", "VIP"])
    })
df_customers = pd.DataFrame(customers)
df_customers.to_csv("customers.csv", index=False)

# 2. Products CSV
categories = {
    "Electronics": ["Mobiles", "Laptops", "Accessories"],
    "Clothing": ["Men", "Women", "Kids"],
    "Home": ["Furniture", "Decor", "Kitchen"],
    "Books": ["Fiction", "Tech", "History"]
}
products = []
for i in range(1, 51):
    pid = f"PROD_{i:03d}"
    cat = random.choice(list(categories.keys()))
    subcat = random.choice(categories[cat])
    pname = f" {fake.word().title()} {subcat} " if random.random() < 0.2 else f"{fake.word().title()} {subcat}"
    
    products.append({
        "product_id": pid,
        "product_name": pname,
        "category": cat,
        "subcategory": subcat,
        "cost_price": round(random.uniform(10, 500), 2)
    })
df_products = pd.DataFrame(products)
df_products.to_csv("products.csv", index=False)

# 3. Orders CSV
statuses = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
regions = ["US-EAST", "US-WEST", "EU-CENTRAL", "APAC-SOUTH"]
orders = []
for i in range(1, 601):
    oid = f"ORD_{i:05d}"
    # 5% NULL customer_id
    cid = None if random.random() < 0.05 else random.choice(customer_ids)
    
    dt = fake.date_time_between(start_date="-1y", end_date="now")
    # Wrong format for some dates
    date_str = dt.strftime("%d-%m-%Y") if random.random() < 0.05 else dt.strftime("%Y-%m-%d %H:%M:%S")
    
    orders.append({
        "order_id": oid,
        "customer_id": cid,
        "order_date": date_str,
        "status": random.choice(statuses),
        "region_code": random.choice(regions)
    })
df_orders = pd.DataFrame(orders)
df_orders.to_csv("orders.csv", index=False)

# 4. Order Items CSV
order_items = []
item_id = 1
for order in orders:
    num_items = random.randint(1, 4)
    for _ in range(num_items):
        qty = random.randint(1, 5)
        # 3% negative quantity
        if random.random() < 0.03:
            qty = -qty
            
        order_items.append({
            "item_id": f"ITEM_{item_id:06d}",
            "order_id": order["order_id"],
            "product_id": random.choice(products)["product_id"],
            "quantity": qty,
            "unit_price": round(random.uniform(15, 600), 2),
            "discount_percent": random.choice([0, 5, 10, 15, 20])
        })
        item_id += 1

df_items = pd.DataFrame(order_items)
df_items.to_csv("order_items.csv", index=False)

print("Data generation complete! 4 CSV files created.")