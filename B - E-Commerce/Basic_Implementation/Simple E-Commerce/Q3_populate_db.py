import sqlite3
import random

DB_NAME = "B - E-Commerce/Simple E-Commerce/ecommerce.db"

# Connect to the database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ---------------------- POPULATE PRODUCTS TABLE ----------------------
products = [
    ("Laptop", "High-performance laptop", 1200.99, "Electronics", 15),
    ("Smartphone", "Latest model smartphone", 799.99, "Electronics", 25),
    ("Headphones", "Noise-canceling headphones", 199.99, "Accessories", 30),
    ("Gaming Console", "Next-gen gaming console", 499.99, "Electronics", 10),
    ("Coffee Maker", "Automatic coffee machine", 99.99, "Home Appliances", 20),
    ("Desk Chair", "Ergonomic office chair", 150.50, "Furniture", 12),
    ("Backpack", "Waterproof travel backpack", 49.99, "Accessories", 35),
    ("Smart Watch", "Fitness and health tracking watch", 249.99, "Wearables", 18),
    ("LED TV", "55-inch 4K UHD Smart TV", 649.99, "Electronics", 8),
    ("Bluetooth Speaker", "Portable wireless speaker", 89.99, "Accessories", 22),
]

cursor.executemany("INSERT INTO products (name, description, price, category, stock) VALUES (?, ?, ?, ?, ?);", products)

# ---------------------- POPULATE ORDERS TABLE ----------------------
orders = []
for i in range(1, 11):  # Create 10 orders
    user_id = random.randint(1, 5)  # Assuming 5 users
    total_price = round(random.uniform(50, 2000), 2)
    status = random.choice(["Pending", "Completed", "Shipped", "Canceled"])
    orders.append((user_id, total_price, status))

cursor.executemany("INSERT INTO orders (user_id, total_price, status) VALUES (?, ?, ?);", orders)

# ---------------------- POPULATE ORDER ITEMS TABLE ----------------------
order_items = []
for order_id in range(1, 11):  # Assume 10 orders exist
    for _ in range(random.randint(1, 4)):  # Each order has 1-4 products
        product_id = random.randint(1, len(products))
        quantity = random.randint(1, 3)
        order_items.append((order_id, product_id, quantity))

cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?);", order_items)

# ---------------------- POPULATE CART TABLE ----------------------
cart = []
for user_id in range(1, 6):  # Assuming 5 users
    for _ in range(random.randint(2, 5)):  # Each user has 2-5 products in cart
        product_id = random.randint(1, len(products))
        quantity = random.randint(1, 3)
        cart.append((user_id, product_id, quantity))

cursor.executemany("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);", cart)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database populated successfully!")
