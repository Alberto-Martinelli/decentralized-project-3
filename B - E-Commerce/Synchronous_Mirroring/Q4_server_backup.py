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

# Define primary and mirrored databases
PRIMARY_DB = "ecommerce_primary.db"
MIRROR_DB = "ecommerce_mirror.db"

def db_connection(db_path):
    """Create a connection to the given database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  
    return conn

def execute_write(query, params=()):
    """Write to both primary and mirrored databases (ensuring consistency)."""
    try:
        conn_primary = db_connection(PRIMARY_DB)
        conn_mirror = db_connection(MIRROR_DB)

        cursor_primary = conn_primary.cursor()
        cursor_mirror = conn_mirror.cursor()

        cursor_primary.execute(query, params)
        cursor_mirror.execute(query, params)

        conn_primary.commit()
        conn_mirror.commit()

        conn_primary.close()
        conn_mirror.close()

        return True  # Success
    except Exception as e:
        print(f"Database write error: {e}")
        return False

# ----------------------------------------- PRODUCTS ROUTES -----------------------------------------

@app.route('/products', methods=['GET'])
def get_products():
    conn = db_connection(PRIMARY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    conn = db_connection(PRIMARY_DB)
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

    query = "INSERT INTO products (name, description, price, category, stock) VALUES (?, ?, ?, ?, ?);"
    if execute_write(query, (data["name"], data["description"], data["price"], data["category"], data["stock"])):
        return jsonify({"message": "Product added successfully"}), 201
    else:
        return jsonify({"error": "Database write failed"}), 500

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    update_fields = {key: data[key] for key in ["name", "description", "price", "category", "stock"] if key in data}

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    query = "UPDATE products SET " + ", ".join(f"{key} = ?" for key in update_fields.keys()) + " WHERE id = ?"
    values = list(update_fields.values()) + [product_id]

    if execute_write(query, values):
        return jsonify({"message": "Product updated successfully"})
    else:
        return jsonify({"error": "Database update failed"}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = db_connection(PRIMARY_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM order_items WHERE product_id = ?", (product_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Cannot delete a product that is part of an order"}), 400

    cursor.execute("SELECT 1 FROM cart WHERE product_id = ?", (product_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Cannot delete a product that is in a user's cart"}), 400

    if execute_write("DELETE FROM products WHERE id = ?", (product_id,)):
        return jsonify({"message": "Product deleted successfully"})
    else:
        return jsonify({"error": "Database deletion failed"}), 500

# ----------------------------------------- CART ROUTES -----------------------------------------

@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity or quantity <= 0:
        return jsonify({"error": "Invalid product_id or quantity"}), 400

    query = "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);"
    if execute_write(query, (user_id, product_id, quantity)):
        return jsonify({"message": "Product added to cart"})
    else:
        return jsonify({"error": "Database write failed"}), 500

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    conn = db_connection(PRIMARY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cart WHERE user_id = ?", (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in cart_items])

# ----------------------------------------- ORDERS ROUTES -----------------------------------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    cart_items = data.get("cart_items")

    if not user_id or not cart_items:
        return jsonify({"error": "Missing user_id or cart_items"}), 400

    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    query = "INSERT INTO orders (user_id, total_price) VALUES (?, ?);"

    if execute_write(query, (user_id, total_price)):
        return jsonify({"message": "Order created successfully"})
    else:
        return jsonify({"error": "Database write failed"}), 500

@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    conn = db_connection(PRIMARY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ?;", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

if __name__ == '__main__':
    PORT = 3002
    print(f"Server is running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
