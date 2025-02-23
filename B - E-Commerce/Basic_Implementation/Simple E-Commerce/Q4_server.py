from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

DB_NAME = "B - E-Commerce/Simple E-Commerce/ecommerce.db"

def db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn

# ----------------------------------------- PRODUCTS ROUTES -----------------------------------------

@app.route('/products', methods=['GET'])
def get_products():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return jsonify(dict(product)) if product else jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    required_fields = ["name", "description", "price", "category", "stock"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, description, price, category, stock) 
        VALUES (?, ?, ?, ?, ?);
    """, (data["name"], data["description"], data["price"], data["category"], data["stock"]))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    update_fields = {key: data[key] for key in ["name", "description", "price", "category", "stock"] if key in data}

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    query = "UPDATE products SET " + ", ".join(f"{key} = ?" for key in update_fields.keys()) + " WHERE id = ?"
    values = list(update_fields.values()) + [product_id]

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    return jsonify({"message": "Product updated successfully"})

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM order_items WHERE product_id = ?", (product_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Cannot delete a product that is part of an order"}), 400

    cursor.execute("SELECT 1 FROM cart WHERE product_id = ?", (product_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Cannot delete a product that is in a user's cart"}), 400

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted successfully"})

# ----------------------------------------- CART ROUTES -----------------------------------------

@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity or quantity <= 0:
        return jsonify({"error": "Invalid product_id or quantity"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        return jsonify({"error": "Product not found"}), 400

    cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);", (user_id, product_id, quantity))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added to cart"})

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, p.name, c.quantity, p.price, 
               (p.price * c.quantity) AS total_item_price
        FROM cart c 
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?;
    """, (user_id,))
    cart_items = cursor.fetchall()
    conn.close()

    return jsonify([dict(item) for item in cart_items])

@app.route('/cart/<int:user_id>/item/<int:product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?;", (user_id, product_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product removed from cart"})

# ----------------------------------------- ORDERS ROUTES -----------------------------------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    cart_items = data.get("cart_items")

    if not user_id or not cart_items:
        return jsonify({"error": "Missing user_id or cart_items"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    total_price = sum(item["quantity"] * item["price"] for item in cart_items)
    cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (?, ?);", (user_id, total_price))
    order_id = cursor.lastrowid

    for item in cart_items:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?);",
                       (order_id, item["product_id"], item["quantity"]))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order created successfully", "order_id": order_id})

@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ?;", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

if __name__ == '__main__':
    PORT = 3001
    print(f"Server is running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
