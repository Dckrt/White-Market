from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import oracledb, os, json

oracledb.init_oracle_client(
    lib_dir=r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_26"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "oracle+oracledb://dotado:202400926@localhost:1521/?service_name=XE"
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/*": {"origins": "*"}})
ADMIN_PASSWORD = "adnu_admin_2024"

# ── HELPERS ───────────────────────────────────────────────────────────────────

def save_image(file):
    if not file or file.filename == '':
        return None
    filename = f"{os.urandom(8).hex()}_{file.filename.replace(' ', '_')}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return f"/static/uploads/{filename}"

def save_images(files):
    """Save multiple images, return JSON array string of URLs."""
    urls = []
    for file in files:
        url = save_image(file)
        if url:
            urls.append(url)
    return json.dumps(urls) if urls else None

def full_url(path):
    if not path:
        return None
    return f"http://127.0.0.1:5000{path}"

def parse_images(image_url_raw):
    """Parse image_url field — could be JSON array or single string."""
    if not image_url_raw:
        return []
    try:
        parsed = json.loads(image_url_raw)
        if isinstance(parsed, list):
            return [full_url(u) for u in parsed if u]
        return [full_url(image_url_raw)]
    except Exception:
        return [full_url(image_url_raw)]

def send_notification(user_id, message):
    try:
        db.session.execute(db.text("""
            INSERT INTO NOTIFICATIONS (id, user_id, message, is_read, created_at)
            VALUES (notif_seq.NEXTVAL, :user_id, :msg, 0, SYSDATE)
        """), {"user_id": user_id, "msg": message})
        db.session.commit()
    except Exception as e:
        print("NOTIFICATION ERROR:", e)
        db.session.rollback()

def track_price(product_id, price):
    """Insert a price history record."""
    try:
        db.session.execute(db.text("""
            INSERT INTO PRICE_HISTORY (id, product_id, price, recorded_at)
            VALUES (price_hist_seq.NEXTVAL, :pid, :price, SYSDATE)
        """), {"pid": product_id, "price": price})
        db.session.commit()
    except Exception as e:
        print("PRICE HISTORY ERROR (non-fatal):", e)
        db.session.rollback()

# ── ROOT ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "White Market Backend running!"

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data       = request.get_json()
    email      = data.get("email", "")
    student_id = data.get("student_id_number", "")
    if not email.endswith("@gbox.adnu.edu.ph"):
        return jsonify({"message": "Use ADNU GBOX email only"}), 400
    if "-" not in student_id:
        return jsonify({"message": "Student ID must contain '-'"}), 400
    existing = db.session.execute(
        db.text("SELECT COUNT(*) FROM USERS WHERE email = :email"), {"email": email}
    ).scalar()
    if existing > 0:
        return jsonify({"message": "Email already registered"}), 400
    hashed_pw = bcrypt.generate_password_hash(data.get("password")).decode("utf-8")
    try:
        db.session.execute(db.text("""
            INSERT INTO USERS (id, name, email, password_hash,
                student_id_number, course, year_level, department)
            VALUES (users_seq.NEXTVAL, :name, :email, :pw,
                :student_id, :course, :year, :dept)
        """), {
            "name": data.get("name"), "email": email, "pw": hashed_pw,
            "student_id": student_id, "course": data.get("course"),
            "year": data.get("year_level"), "dept": data.get("department")
        })
        db.session.commit()
        return jsonify({"message": "Registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    res  = db.session.execute(db.text("""
        SELECT id, name, email, password_hash,
               student_id_number, course, year_level, department
        FROM USERS WHERE email = :email
    """), {"email": data.get("email")}).fetchone()
    if not res:
        return jsonify({"message": "User not found"}), 404
    if bcrypt.check_password_hash(str(res[3]), data.get("password")):
        return jsonify({
            "user_id": res[0], "name": res[1], "email": res[2],
            "student_id_number": res[4], "course": res[5],
            "year_level": res[6], "department": res[7]
        })
    return jsonify({"message": "Invalid password"}), 401

# ── PRODUCTS ──────────────────────────────────────────────────────────────────

@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        seller_id = request.args.get("seller_id")
        search    = request.args.get("search", "").strip()
        category  = request.args.get("category", "")
        tag       = request.args.get("tag", "")
        sort      = request.args.get("sort", "newest")  # newest, oldest, price_asc, price_desc, name_asc, name_desc

        base_select = """
            SELECT p.id, p.title, p.description, p.price, p.category,
                   p.status, p.seller_id, p.image_url, u.name AS seller_name,
                   p.tags, p.created_at
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
        """

        order_map = {
            "newest":     "p.id DESC",
            "oldest":     "p.id ASC",
            "price_asc":  "p.price ASC",
            "price_desc": "p.price DESC",
            "name_asc":   "p.title ASC",
            "name_desc":  "p.title DESC",
        }
        order_clause = order_map.get(sort, "p.id DESC")

        params = {}

        if seller_id:
            query = base_select + " WHERE p.seller_id = :seller_id ORDER BY " + order_clause
            params["seller_id"] = int(seller_id)
        else:
            conditions = ["p.status = 'Available'"]
            if search:
                conditions.append("(LOWER(p.title) LIKE :search OR LOWER(p.description) LIKE :search OR LOWER(p.tags) LIKE :search)")
                params["search"] = f"%{search.lower()}%"
            if category:
                conditions.append("p.category = :category")
                params["category"] = category
            if tag:
                conditions.append("LOWER(p.tags) LIKE :tag")
                params["tag"] = f"%{tag.lower()}%"
            where = " WHERE " + " AND ".join(conditions)
            query = base_select + where + " ORDER BY " + order_clause

        result = db.session.execute(db.text(query), params)
        products = []
        for row in result:
            images = parse_images(row[7])
            products.append({
                "id":          row[0],
                "title":       row[1],
                "description": row[2],
                "price":       float(row[3]),
                "category":    row[4],
                "status":      row[5],
                "seller_id":   row[6],
                "image_url":   images[0] if images else None,
                "images":      images,
                "seller_name": row[8],
                "tags":        row[9].split(",") if row[9] else [],
                "created_at":  str(row[10]) if row[10] else None,
            })
        return jsonify(products)
    except Exception as e:
        print("GET PRODUCTS ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        res = db.session.execute(db.text("""
            SELECT p.id, p.title, p.description, p.price, p.category,
                   p.status, p.created_at, u.name AS seller_name,
                   p.seller_id, p.image_url, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
            WHERE p.id = :id
        """), {"id": product_id}).fetchone()
        if not res:
            return jsonify({"message": "Product not found"}), 404
        images = parse_images(res[9])
        return jsonify({
            "id":          res[0],
            "title":       res[1],
            "description": res[2],
            "price":       float(res[3]),
            "category":    res[4],
            "status":      res[5],
            "created_at":  str(res[6]) if res[6] else None,
            "seller_name": res[7],
            "seller_id":   res[8],
            "image_url":   images[0] if images else None,
            "images":      images,
            "tags":        res[10].split(",") if res[10] else [],
        })
    except Exception as e:
        print("GET PRODUCT ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/products", methods=["POST"])
def create_product():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            title       = request.form.get("title")
            description = request.form.get("description")
            price       = float(request.form.get("price", 0))
            category    = request.form.get("category", "General")
            seller_id   = request.form.get("user_id")
            tags        = request.form.get("tags", "")
            # Support multiple images
            files = request.files.getlist("images") or request.files.getlist("image")
            if files:
                image_url = save_images(files)
            else:
                image_url = None
        else:
            data        = request.get_json()
            title       = data.get("title")
            description = data.get("description")
            price       = float(data.get("price", 0))
            category    = data.get("category", "General")
            seller_id   = data.get("user_id")
            tags        = data.get("tags", "")
            image_url   = None

        # Get product id after insert
        new_id = db.session.execute(db.text("SELECT products_seq.NEXTVAL FROM DUAL")).scalar()
        db.session.execute(db.text("""
            INSERT INTO PRODUCTS (id, title, description, price,
                category, seller_id, created_at, status, image_url, tags)
            VALUES (:id, :title, :description, :price,
                :category, :seller_id, SYSDATE, 'Available', :image_url, :tags)
        """), {
            "id": new_id, "title": title, "description": description,
            "price": price, "category": category, "seller_id": seller_id,
            "image_url": image_url, "tags": tags
        })
        db.session.commit()
        # Track initial price
        track_price(new_id, price)
        return jsonify({"message": "Product created successfully", "id": new_id}), 201
    except Exception as e:
        db.session.rollback()
        print("PRODUCT ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            user_id     = request.form.get("user_id")
            title       = request.form.get("title")
            description = request.form.get("description")
            price       = float(request.form.get("price", 0))
            category    = request.form.get("category")
            tags        = request.form.get("tags", "")
            files       = request.files.getlist("images") or request.files.getlist("image")
            new_image   = save_images(files) if files and files[0].filename else None
        else:
            data        = request.get_json()
            user_id     = data.get("user_id")
            title       = data.get("title")
            description = data.get("description")
            price       = float(data.get("price", 0))
            category    = data.get("category")
            tags        = data.get("tags", "")
            new_image   = None

        owner = db.session.execute(
            db.text("SELECT seller_id, price FROM PRODUCTS WHERE id = :id"), {"id": product_id}
        ).fetchone()
        if not owner or int(owner[0]) != int(user_id):
            return jsonify({"message": "Unauthorized"}), 403

        old_price = float(owner[1])

        if new_image:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:title, description=:description,
                    price=:price, category=:category, image_url=:image_url, tags=:tags WHERE id=:id
            """), {"title": title, "description": description, "price": price,
                   "category": category, "image_url": new_image, "tags": tags, "id": product_id})
        else:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:title, description=:description,
                    price=:price, category=:category, tags=:tags WHERE id=:id
            """), {"title": title, "description": description, "price": price,
                   "category": category, "tags": tags, "id": product_id})
        db.session.commit()

        # Track price change if price changed
        if price != old_price:
            track_price(product_id, price)

        return jsonify({"message": "Product updated successfully"})
    except Exception as e:
        db.session.rollback()
        print("UPDATE PRODUCT ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    user_id = request.args.get("user_id")
    try:
        owner = db.session.execute(
            db.text("SELECT seller_id FROM PRODUCTS WHERE id = :id"), {"id": product_id}
        ).scalar()
        if not owner or int(owner) != int(user_id):
            return jsonify({"message": "Unauthorized"}), 403
        db.session.execute(db.text("DELETE FROM CART WHERE product_id = :id"), {"id": product_id})
        db.session.execute(db.text("DELETE FROM PRICE_HISTORY WHERE product_id = :id"), {"id": product_id})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE id = :id"), {"id": product_id})
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── PRICE HISTORY ─────────────────────────────────────────────────────────────

@app.route("/api/products/<int:product_id>/price-history", methods=["GET"])
def get_price_history(product_id):
    try:
        result = db.session.execute(db.text("""
            SELECT price, recorded_at FROM PRICE_HISTORY
            WHERE product_id = :pid
            ORDER BY recorded_at ASC
        """), {"pid": product_id})
        history = [{"price": float(r[0]), "date": str(r[1])} for r in result]
        return jsonify(history)
    except Exception as e:
        print("PRICE HISTORY ERROR:", e)
        return jsonify([])

# ── TAGS ──────────────────────────────────────────────────────────────────────

@app.route("/api/tags", methods=["GET"])
def get_all_tags():
    """Return all unique tags used across products."""
    try:
        result = db.session.execute(db.text("""
            SELECT tags FROM PRODUCTS WHERE tags IS NOT NULL AND status = 'Available'
        """))
        tag_set = set()
        for row in result:
            if row[0]:
                for t in row[0].split(","):
                    t = t.strip()
                    if t:
                        tag_set.add(t)
        return jsonify(sorted(list(tag_set)))
    except Exception as e:
        return jsonify([])

# ── COMPARE BY TAG ────────────────────────────────────────────────────────────

@app.route("/api/products/compare", methods=["GET"])
def compare_by_tag():
    """Get all products with a given tag for price comparison."""
    tag = request.args.get("tag", "")
    if not tag:
        return jsonify([])
    try:
        result = db.session.execute(db.text("""
            SELECT p.id, p.title, p.price, p.image_url, u.name AS seller_name, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
            WHERE LOWER(p.tags) LIKE :tag AND p.status = 'Available'
            ORDER BY p.price ASC
        """), {"tag": f"%{tag.lower()}%"})
        items = []
        for row in result:
            images = parse_images(row[3])
            items.append({
                "id": row[0], "title": row[1], "price": float(row[2]),
                "image_url": images[0] if images else None,
                "seller_name": row[4],
                "tags": row[5].split(",") if row[5] else []
            })
        return jsonify(items)
    except Exception as e:
        return jsonify([])

# ── CART ──────────────────────────────────────────────────────────────────────

@app.route("/api/cart", methods=["GET"])
def get_cart():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "user_id required"}), 400
    try:
        result = db.session.execute(db.text("""
            SELECT c.id, p.id, p.title, p.price, p.category,
                   p.status, p.seller_id, u.name, p.image_url, c.quantity
            FROM CART c
            JOIN PRODUCTS p ON c.product_id = p.id
            JOIN USERS u ON p.seller_id = u.id
            WHERE c.user_id = :user_id
        """), {"user_id": int(user_id)})
        items = []
        for row in result:
            images = parse_images(row[8])
            items.append({
                "cart_id": row[0], "id": row[1], "title": row[2],
                "price": float(row[3]), "category": row[4], "status": row[5],
                "seller_id": row[6], "seller_name": row[7],
                "image_url": images[0] if images else None,
                "images": images,
                "quantity": row[9] or 1
            })
        return jsonify(items)
    except Exception as e:
        print("GET CART ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data       = request.get_json()
    user_id    = data.get("user_id")
    product_id = data.get("product_id")
    try:
        owner = db.session.execute(
            db.text("SELECT seller_id FROM PRODUCTS WHERE id = :id"), {"id": product_id}
        ).scalar()
        if owner and int(owner) == int(user_id):
            return jsonify({"message": "You cannot add your own product to cart"}), 400
        existing = db.session.execute(db.text("""
            SELECT COUNT(*) FROM CART WHERE user_id=:user_id AND product_id=:product_id
        """), {"user_id": user_id, "product_id": product_id}).scalar()
        if existing > 0:
            return jsonify({"message": "Already in cart"}), 400
        db.session.execute(db.text("""
            INSERT INTO CART (id, user_id, product_id, quantity)
            VALUES (cart_seq.NEXTVAL, :user_id, :product_id, 1)
        """), {"user_id": user_id, "product_id": product_id})
        db.session.commit()
        buyer = db.session.execute(
            db.text("SELECT name FROM USERS WHERE id = :id"), {"id": user_id}
        ).scalar()
        product_title = db.session.execute(
            db.text("SELECT title FROM PRODUCTS WHERE id = :id"), {"id": product_id}
        ).scalar()
        if owner:
            send_notification(owner, f"{buyer} added your product '{product_title}' to their cart!")
        return jsonify({"message": "Added to cart"}), 201
    except Exception as e:
        db.session.rollback()
        print("ADD CART ERROR:", e)
        return jsonify({"message": "Server error"}), 500

@app.route("/api/cart/<int:cart_id>", methods=["DELETE"])
def remove_from_cart(cart_id):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE id = :id"), {"id": cart_id})
        db.session.commit()
        return jsonify({"message": "Removed from cart"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── CHECKOUT ──────────────────────────────────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data       = request.get_json()
    user_id    = data.get("user_id")
    cart_id    = data.get("cart_id")
    product_id = data.get("product_id")
    try:
        if cart_id:
            db.session.execute(
                db.text("DELETE FROM CART WHERE id = :cart_id AND user_id = :user_id"),
                {"cart_id": cart_id, "user_id": user_id}
            )
        if product_id:
            prod = db.session.execute(
                db.text("SELECT seller_id, title FROM PRODUCTS WHERE id = :id"),
                {"id": product_id}
            ).fetchone()
            if prod:
                buyer = db.session.execute(
                    db.text("SELECT name FROM USERS WHERE id = :id"), {"id": user_id}
                ).scalar()
                send_notification(prod[0], f"{buyer} placed an order for '{prod[1]}'!")
        db.session.commit()
        return jsonify({"message": "Order placed successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── MESSAGES ──────────────────────────────────────────────────────────────────

@app.route("/api/messages", methods=["POST"])
def send_message():
    data         = request.get_json()
    sender_id    = int(data.get("sender_id"))
    receiver_id  = int(data.get("receiver_id"))
    message_text = data.get("message_text") or data.get("content") or data.get("message")
    product_id   = data.get("product_id", None)
    try:
        db.session.execute(db.text("""
            INSERT INTO MESSAGES (id, sender_id, receiver_id, product_id, message, sent_at, is_read)
            VALUES (messages_seq.NEXTVAL, :sender, :receiver, :product_id, :message, SYSDATE, 0)
        """), {"sender": sender_id, "receiver": receiver_id,
               "product_id": product_id, "message": message_text})
        db.session.commit()
        sender_name = db.session.execute(
            db.text("SELECT name FROM USERS WHERE id = :id"), {"id": sender_id}
        ).scalar()
        send_notification(receiver_id, f"New message from {sender_name}")
        return jsonify({"message": "Message sent"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages", methods=["GET"])
def get_messages():
    try:
        sender   = int(request.args.get("sender_id"))
        receiver = int(request.args.get("receiver_id"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid sender_id or receiver_id"}), 400
    try:
        result = db.session.execute(db.text("""
            SELECT sender_id, receiver_id, message, sent_at
            FROM MESSAGES
            WHERE (sender_id = :sender AND receiver_id = :receiver)
               OR (sender_id = :receiver AND receiver_id = :sender)
            ORDER BY sent_at ASC
        """), {"sender": sender, "receiver": receiver})
        return jsonify([{
            "sender_id": r[0], "receiver_id": r[1],
            "message_text": r[2], "sent_at": str(r[3])
        } for r in result])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/mark-read", methods=["POST"])
def mark_messages_read():
    data      = request.get_json()
    reader_id = data.get("reader_id")
    sender_id = data.get("sender_id")
    try:
        db.session.execute(db.text("""
            UPDATE MESSAGES SET is_read = 1
            WHERE receiver_id = :reader AND sender_id = :sender AND is_read = 0
        """), {"reader": int(reader_id), "sender": int(sender_id)})
        db.session.commit()
        return jsonify({"message": "Messages marked as read"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/threads", methods=["GET"])
def get_threads():
    try:
        user_id = int(request.args.get("user_id"))
    except (TypeError, ValueError):
        return jsonify([])
    try:
        result = db.session.execute(db.text("""
            SELECT DISTINCT
                CASE WHEN m.sender_id = :uid1 THEN m.receiver_id ELSE m.sender_id END AS partner_id,
                u.name AS partner_name
            FROM MESSAGES m
            JOIN USERS u ON u.id = CASE WHEN m.sender_id = :uid2 THEN m.receiver_id ELSE m.sender_id END
            WHERE m.sender_id = :uid3 OR m.receiver_id = :uid4
        """), {"uid1": user_id, "uid2": user_id, "uid3": user_id, "uid4": user_id})
        threads = []
        for row in result:
            partner_id = row[0]
            last = db.session.execute(db.text("""
                SELECT message, sent_at FROM MESSAGES
                WHERE (sender_id = :uid AND receiver_id = :pid)
                   OR (sender_id = :pid AND receiver_id = :uid)
                ORDER BY sent_at DESC FETCH FIRST 1 ROWS ONLY
            """), {"uid": user_id, "pid": partner_id}).fetchone()
            unread = db.session.execute(db.text("""
                SELECT COUNT(*) FROM MESSAGES
                WHERE sender_id = :pid AND receiver_id = :uid AND is_read = 0
            """), {"uid": user_id, "pid": partner_id}).scalar()
            threads.append({
                "seller_id":    partner_id, "seller_name": row[1],
                "last_message": last[0] if last else "",
                "last_time":    str(last[1]) if last else "",
                "unread":       unread > 0
            })
        return jsonify(threads)
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/unread-count", methods=["GET"])
def unread_count():
    try:
        user_id = int(request.args.get("user_id"))
        count = db.session.execute(db.text("""
            SELECT COUNT(*) FROM MESSAGES WHERE receiver_id = :uid AND is_read = 0
        """), {"uid": user_id}).scalar()
        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"count": 0})

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")
    try:
        result = db.session.execute(db.text("""
            SELECT id, message, is_read, created_at FROM NOTIFICATIONS
            WHERE user_id = :user_id ORDER BY created_at DESC
            FETCH FIRST 30 ROWS ONLY
        """), {"user_id": int(user_id)})
        return jsonify([{
            "id": r[0], "message": r[1], "is_read": r[2], "created_at": str(r[3])
        } for r in result])
    except Exception as e:
        return jsonify([])

@app.route("/api/notifications/read", methods=["POST"])
def mark_notifications_read():
    user_id = request.get_json().get("user_id")
    try:
        db.session.execute(db.text("UPDATE NOTIFICATIONS SET is_read=1 WHERE user_id=:uid"), {"uid": user_id})
        db.session.commit()
        return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── SELLER PAYMENT ────────────────────────────────────────────────────────────

@app.route("/api/users/<int:user_id>/payment", methods=["GET"])
def get_seller_payment(user_id):
    try:
        res = db.session.execute(
            db.text("SELECT gcash_number, bank_details FROM USERS WHERE id = :id"), {"id": user_id}
        ).fetchone()
        return jsonify({"gcash": res[0] if res else None, "bank": res[1] if res else None})
    except:
        return jsonify({"gcash": None, "bank": None})

@app.route("/api/users/<int:user_id>/payment", methods=["PUT"])
def update_seller_payment(user_id):
    data = request.get_json()
    try:
        db.session.execute(db.text("""
            UPDATE USERS SET gcash_number = :gcash, bank_details = :bank WHERE id = :id
        """), {"gcash": data.get("gcash"), "bank": data.get("bank"), "id": user_id})
        db.session.commit()
        return jsonify({"message": "Payment details updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── ADMIN ──────────────────────────────────────────────────────────────────────

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    if request.get_json().get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"message": "Wrong password"}), 401

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    try:
        return jsonify({
            "users":      db.session.execute(db.text("SELECT COUNT(*) FROM USERS")).scalar(),
            "products":   db.session.execute(db.text("SELECT COUNT(*) FROM PRODUCTS")).scalar(),
            "messages":   db.session.execute(db.text("SELECT COUNT(*) FROM MESSAGES")).scalar(),
            "cart_items": db.session.execute(db.text("SELECT COUNT(*) FROM CART")).scalar(),
        })
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    try:
        result = db.session.execute(db.text("""
            SELECT id, name, email, student_id_number, course, department, year_level
            FROM USERS ORDER BY id DESC
        """))
        return jsonify([{
            "id": r[0], "name": r[1], "email": r[2], "student_id": r[3],
            "course": r[4], "department": r[5], "year_level": r[6]
        } for r in result])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products", methods=["GET"])
def admin_products():
    try:
        result = db.session.execute(db.text("""
            SELECT p.id, p.title, p.price, p.category, p.status,
                   p.created_at, u.name AS seller_name, p.image_url, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
            ORDER BY p.id DESC
        """))
        products = []
        for r in result:
            images = parse_images(r[7])
            products.append({
                "id": r[0], "title": r[1], "price": float(r[2]),
                "category": r[3], "status": r[4],
                "created_at": str(r[5]) if r[5] else None,
                "seller_name": r[6],
                "image_url": images[0] if images else None,
                "tags": r[8].split(",") if r[8] else []
            })
        return jsonify(products)
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def admin_delete_product(product_id):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE product_id = :id"), {"id": product_id})
        db.session.execute(db.text("DELETE FROM PRICE_HISTORY WHERE product_id = :id"), {"id": product_id})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE id = :id"), {"id": product_id})
        db.session.commit()
        return jsonify({"message": "Product deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE user_id = :id"), {"id": user_id})
        db.session.execute(db.text("DELETE FROM MESSAGES WHERE sender_id=:id OR receiver_id=:id"), {"id": user_id})
        db.session.execute(db.text("DELETE FROM NOTIFICATIONS WHERE user_id = :id"), {"id": user_id})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE seller_id = :id"), {"id": user_id})
        db.session.execute(db.text("DELETE FROM USERS WHERE id = :id"), {"id": user_id})
        db.session.commit()
        return jsonify({"message": "User deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    try:
        result = db.session.execute(db.text("""
            SELECT m.id, m.sender_id, m.receiver_id, m.message,
                   m.sent_at, m.is_read, u1.name, u2.name
            FROM MESSAGES m
            LEFT JOIN USERS u1 ON m.sender_id = u1.id
            LEFT JOIN USERS u2 ON m.receiver_id = u2.id
            ORDER BY m.sent_at DESC FETCH FIRST 200 ROWS ONLY
        """))
        return jsonify([{
            "id": r[0], "sender_id": r[1], "receiver_id": r[2],
            "message": r[3], "sent_at": str(r[4]) if r[4] else None,
            "is_read": r[5], "sender_name": r[6] or str(r[1]),
            "receiver_name": r[7] or str(r[2])
        } for r in result])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)