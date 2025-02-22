from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS


app = Flask(__name__)
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

# GET /products - List all products (with optional filtering)
@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    in_stock = request.args.get('inStock')

    conn = db_connection()
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
    conn = db_connection()
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

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, description, price, category, stock) 
        VALUES (?, ?, ?, ?, ?);
    """, (data["name"], data["description"], data["price"], data["category"], data["stock"]))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully"}), 201

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

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(update_query, values)
    conn.commit()
    conn.close()

    return jsonify({"message": "Product updated successfully"})

# DELETE /products/:id - Remove a product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted successfully"})


# ----------------------------------------- CART ROUTES -----------------------------------------

# POST /cart/:userId - Add product to cart
@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);", (user_id, product_id, quantity))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added to cart"})

# GET /cart/:userId - Retrieve user cart
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    conn = db_connection()
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
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?;", (user_id, product_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product removed from cart"})


# ----------------------------------------- ORDERS ROUTES -----------------------------------------

# POST /orders - Create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    cart_items = data.get("cart_items")

    if not user_id or not cart_items:
        return jsonify({"error": "Missing user_id or cart_items"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    # Calculate total price
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    # Create order
    cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (?, ?);", (user_id, total_price))
    order_id = cursor.lastrowid

    # Insert order items
    for item in cart_items:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?);",
                       (order_id, item["product_id"], item["quantity"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order created successfully", "order_id": order_id})

# GET /orders/:userId - Get orders for a user
@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ?;", (user_id,))
    orders = cursor.fetchall()
    conn.close()

    return jsonify([dict(order) for order in orders])


if __name__ == '__main__':
    PORT = 3002
    print(f"Server is running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)