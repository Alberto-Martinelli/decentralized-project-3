from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from pathlib import Path

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
script_dir = Path(__file__).parent.absolute()
PRIMARY_DB = script_dir / "ecommerce_primary.db"
MIRROR_DB = script_dir / "ecommerce_mirror.db"


def db_connection(db_path):
    """Create a connection to the given database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  
    return conn

def execute_write(query, params=()):
    """Write to both primary and mirrored databases."""
    try:
        # Write to Primary DB
        conn_primary = db_connection(PRIMARY_DB)
        cursor_primary = conn_primary.cursor()
        cursor_primary.execute(query, params)
        conn_primary.commit()
        conn_primary.close()

        # Write to Mirror DB
        conn_mirror = db_connection(MIRROR_DB)
        cursor_mirror = conn_mirror.cursor()
        cursor_mirror.execute(query, params)
        conn_mirror.commit()
        conn_mirror.close()

        return True  # Success
    except Exception as e:
        print(f"Database write error: {e}")
        return False

# ----------------------------------------- PRODUCTS ROUTES -----------------------------------------

# GET /test-connection - Test the connection to the server
@app.route('/test-connection', methods=['GET'])
def test_connection():
    return jsonify({"message": "Connection successful"}), 200

# GET /products - List all products (with optional filtering)
@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    in_stock = request.args.get('inStock')
    
    try:
        conn = db_connection(PRIMARY_DB)
    except:
        conn = db_connection(MIRROR_DB)  # Failover to mirror
    
    cursor = conn.cursor()
    query = "SELECT * FROM products"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)
    
    if in_stock and in_stock.lower() == 'true':
        query += " AND stock > 0" if category else " WHERE stock > 0"
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in products])

# GET /products/:id - Retrieve a single product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        conn = db_connection(PRIMARY_DB)
    except:
        conn = db_connection(MIRROR_DB)  # Failover to mirror
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        return jsonify(dict(product))
    return jsonify({"error": "Product not found"}), 404

# POST /products - Add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    required_fields = ["name", "description", "price", "category", "stock"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    query = "INSERT INTO products (name, description, price, category, stock) VALUES (?, ?, ?, ?, ?);"
    params = (data["name"], data["description"], data["price"], data["category"], data["stock"])

    if execute_write(query, params):
        return jsonify({"message": "Product added successfully"}), 201
    else:
        return jsonify({"error": "Database write failed"}), 500

# PUT /products/:id - Update product details
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    update_fields = []

    for field in ["name", "description", "price", "category", "stock"]:
        if field in data:
            update_fields.append(f"{field} = ?")

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
    values = list(data.values()) + [product_id]

    if execute_write(update_query, values):
        return jsonify({"message": "Product updated successfully"})
    else:
        return jsonify({"error": "Database update failed"}), 500

# DELETE /products/:id - Remove a product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    query = "DELETE FROM products WHERE id = ?"
    
    if execute_write(query, (product_id,)):
        return jsonify({"message": "Product deleted successfully"})
    else:
        return jsonify({"error": "Database deletion failed"}), 500

# ----------------------------------------- CART ROUTES -----------------------------------------

# POST /cart/:userId - Add product to cart
@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    query = "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);"
    params = (user_id, product_id, quantity)

    if execute_write(query, params):
        return jsonify({"message": "Product added to cart"})
    else:
        return jsonify({"error": "Database write failed"}), 500

# GET /cart/:userId - Retrieve user cart
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    try:
        conn = db_connection(PRIMARY_DB)
    except:
        conn = db_connection(MIRROR_DB)  # Failover to mirror
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, p.name, c.quantity, p.price 
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?;
    """, (user_id,))
    
    cart_items = cursor.fetchall()
    conn.close()

    return jsonify([dict(item) for item in cart_items])

# DELETE /cart/:userId/item/:productId - Remove item from cart
@app.route('/cart/<int:user_id>/item/<int:product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    query = "DELETE FROM cart WHERE user_id = ? AND product_id = ?;"
    
    if execute_write(query, (user_id, product_id)):
        return jsonify({"message": "Product removed from cart"})
    else:
        return jsonify({"error": "Database deletion failed"}), 500

# ----------------------------------------- ORDERS ROUTES -----------------------------------------

# POST /orders - Create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    cart_items = data.get("cart_items")

    if not user_id or not cart_items:
        return jsonify({"error": "Missing user_id or cart_items"}), 400

    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    query = "INSERT INTO orders (user_id, total_price) VALUES (?, ?);"
    params = (user_id, total_price)

    if execute_write(query, params):
        return jsonify({"message": "Order created successfully"})
    else:
        return jsonify({"error": "Database write failed"}), 500

# GET /orders/:userId - Get orders for a user
@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    try:
        conn = db_connection(PRIMARY_DB)
    except:
        conn = db_connection(MIRROR_DB)  # Failover to mirror
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ?;", (user_id,))
    orders = cursor.fetchall()
    conn.close()

    return jsonify([dict(order) for order in orders])

if __name__ == '__main__':
    PORT = 3002
    print(f"Server is running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
