"""
Authentication & API Service — White Market
Connects to Oracle XE using oracledb (Thick mode via Instant Client).
Compatible with Oracle XE / APEX 2.1 (uses sequences instead of IDENTITY).
"""

import oracledb
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Oracle Instant Client (Thick mode)
oracledb.init_oracle_client(
    lib_dir=r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_26"
)

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
#  Oracle connection config
# ─────────────────────────────────────────────────────────────
DB_USER     = "system"
DB_PASSWORD = "root"
DB_DSN      = "localhost:1521/XE"

def get_connection():
    """Opens and returns a new Oracle DB connection."""
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


# ═══════════════════════════════════════════════════════════════
#  AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/register", methods=["POST"])
def register():
    """Register a new user (buyer or seller)."""
    payload  = request.json
    email    = payload.get("email")
    password = payload.get("password")
    role     = payload.get("role")

    if not email or not password or not role:
        return jsonify({"message": "All fields are required."}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = :email", {"email": email})
            if cur.fetchone():
                return jsonify({"message": "User already exists."}), 400

            cur.execute(
                "INSERT INTO users (id, email, password, role) "
                "VALUES (users_seq.NEXTVAL, :email, :password, :role)",
                {"email": email, "password": password, "role": role}
            )
            conn.commit()

    return jsonify({"message": "User registered successfully."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate a user and return their info."""
    payload  = request.json
    email    = payload.get("email")
    password = payload.get("password")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email, role FROM users WHERE email = :email AND password = :password",
                {"email": email, "password": password}
            )
            row = cur.fetchone()

    if row:
        user = {"email": row[0], "role": row[1]}
        return jsonify({"message": "Login successful.", "user": user}), 200

    return jsonify({"message": "Invalid email or password."}), 401


# ═══════════════════════════════════════════════════════════════
#  PRODUCT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/products", methods=["GET"])
def get_products():
    """Return all products (for browse / home page)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price, category, image_data, status, owner_email "
                "FROM products ORDER BY created_at DESC"
            )
            cols = ["id", "name", "price", "category", "image", "status", "owner"]
            products = [dict(zip(cols, row)) for row in cur.fetchall()]

    return jsonify(products), 200


@app.route("/api/products", methods=["POST"])
def add_product():
    """Seller adds a new product listing."""
    payload  = request.json
    name     = payload.get("name")
    price    = payload.get("price")
    category = payload.get("category")
    image    = payload.get("image", "")
    owner    = payload.get("owner")

    if not all([name, price, category, owner]):
        return jsonify({"message": "All fields are required."}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (id, name, price, category, image_data, owner_email) "
                "VALUES (products_seq.NEXTVAL, :name, :price, :category, :image, :owner)",
                {"name": name, "price": price, "category": category,
                 "image": image, "owner": owner}
            )
            conn.commit()

    return jsonify({"message": "Product added."}), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Seller edits a product (name, price, status)."""
    payload = request.json

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE products SET name = :name, price = :price, status = :status "
                "WHERE id = :id",
                {"name": payload.get("name"), "price": payload.get("price"),
                 "status": payload.get("status"), "id": product_id}
            )
            conn.commit()

    return jsonify({"message": "Product updated."}), 200


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Seller deletes a product listing."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = :id", {"id": product_id})
            conn.commit()

    return jsonify({"message": "Product deleted."}), 200


# ═══════════════════════════════════════════════════════════════
#  REQUEST / ORDER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/requests", methods=["POST"])
def place_request():
    """Buyer places an order request for a product."""
    payload = request.json

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO requests
                   (id, product_id, buyer_email, seller_email, meet_date,
                    time_range, location, payment_method)
                   VALUES (requests_seq.NEXTVAL, :product_id, :buyer, :seller,
                           TO_DATE(:date, 'YYYY-MM-DD'),
                           :time_range, :location, :payment)""",
                {
                    "product_id": payload.get("product_id"),
                    "buyer":      payload.get("buyer"),
                    "seller":     payload.get("seller"),
                    "date":       payload.get("date"),
                    "time_range": payload.get("timeRange"),
                    "location":   payload.get("location"),
                    "payment":    payload.get("payment"),
                }
            )
            conn.commit()

    return jsonify({"message": "Request sent."}), 201


@app.route("/api/requests/seller/<seller_email>", methods=["GET"])
def get_seller_requests(seller_email):
    """Return all requests assigned to a specific seller."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT r.id, p.id, p.name, p.price, p.image_data,
                          r.buyer_email, r.meet_date, r.time_range,
                          r.location, r.payment_method, r.status
                   FROM requests r
                   JOIN products p ON p.id = r.product_id
                   WHERE r.seller_email = :seller
                   ORDER BY r.created_at DESC""",
                {"seller": seller_email}
            )
            rows = cur.fetchall()

    result = []
    for row in rows:
        result.append({
            "id":      row[0],
            "product": {"id": row[1], "name": row[2], "price": row[3], "image": row[4]},
            "buyer":      row[5],
            "date":       str(row[6])[:10] if row[6] else "",
            "timeRange":  row[7],
            "location":   row[8],
            "payment":    row[9],
            "status":     row[10],
        })

    return jsonify(result), 200


@app.route("/api/requests/<int:request_id>", methods=["PUT"])
def update_request_status(request_id):
    """Seller accepts or rejects a request. Accepting also reserves the product."""
    payload = request.json
    status  = payload.get("status")   # 'accepted' or 'rejected'

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE requests SET status = :status WHERE id = :id",
                {"status": status, "id": request_id}
            )

            if status == "accepted":
                cur.execute(
                    "UPDATE products SET status = 'reserved' "
                    "WHERE id = (SELECT product_id FROM requests WHERE id = :id)",
                    {"id": request_id}
                )

            conn.commit()

    return jsonify({"message": f"Request {status}."}), 200


# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)