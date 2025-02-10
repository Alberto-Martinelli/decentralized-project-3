import sqlite3

# Connect to database
conn = sqlite3.connect("B - E-Commerce/Simple E-Commerce/ecommerce.db")
cursor = conn.cursor()

# Sample product data
products = [
    ("Laptop", "High-end gaming laptop", 1200.99, "Electronics", 10),
    ("Smartphone", "Latest smartphone model", 799.49, "Electronics", 15),
    ("Headphones", "Noise-canceling headphones", 199.99, "Accessories", 20),
    ("Chair", "Ergonomic office chair", 150.75, "Furniture", 5)
]

# Insert products
cursor.executemany("""
INSERT INTO products (name, description, price, category, stock) 
VALUES (?, ?, ?, ?, ?);
""", products)

# Commit and close connection
conn.commit()
conn.close()

print("Sample products added successfully!")
