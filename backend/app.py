from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import oracledb, os, json, traceback

# ── Change these to match your machine ────────────────────────────────────────
oracledb.init_oracle_client(
    lib_dir=r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_26"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "oracle+oracledb://dotado:202400926@localhost:1521/?service_name=XE"
app.config["SECRET_KEY"]              = "whitemarket_secret_2024"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"]      = 20 * 1024 * 1024  # 20MB max

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

ADMIN_PASSWORD = "adnu_admin_2024"

# ── HELPERS ───────────────────────────────────────────────────────────────────

def save_image(file):
    if not file or not getattr(file, 'filename', None) or file.filename == '':
        return None
    ext      = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        return None
    filename = f"{os.urandom(8).hex()}{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return f"/static/uploads/{filename}"

def save_images(files):
    urls = [u for u in (save_image(f) for f in files) if u]
    return json.dumps(urls) if urls else None

def abs_url(path):
    if not path:
        return None
    if path.startswith("http"):
        return path
    return f"http://127.0.0.1:5000{path}"

def parse_images(raw):
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [abs_url(u) for u in parsed if u]
        return [abs_url(raw)]
    except Exception:
        return [abs_url(raw)]

def notify(user_id, message):
    try:
        db.session.execute(db.text("""
            INSERT INTO NOTIFICATIONS (id, user_id, message, is_read, created_at)
            VALUES (notif_seq.NEXTVAL, :uid, :msg, 0, SYSDATE)
        """), {"uid": user_id, "msg": message})
        db.session.commit()
    except Exception as e:
        print("NOTIFY ERROR:", e)
        db.session.rollback()

def track_price(product_id, price):
    try:
        db.session.execute(db.text("""
            INSERT INTO PRICE_HISTORY (id, product_id, price, recorded_at)
            VALUES (price_hist_seq.NEXTVAL, :pid, :price, SYSDATE)
        """), {"pid": product_id, "price": price})
        db.session.commit()
    except Exception as e:
        print("PRICE TRACK ERROR:", e)
        db.session.rollback()

# ── ROOT ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "White Market API running!"

@app.route("/static/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ── PUBLIC STATS ──────────────────────────────────────────────────────────────

@app.route("/api/stats")
def public_stats():
    try:
        users    = db.session.execute(db.text("SELECT COUNT(*) FROM USERS")).scalar()
        products = db.session.execute(db.text("SELECT COUNT(*) FROM PRODUCTS WHERE status='Available'")).scalar()
        return jsonify({"users": users, "products": products, "colleges": 6})
    except Exception as e:
        return jsonify({"users": 0, "products": 0, "colleges": 6})

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email      = (data.get("email") or "").strip()
    student_id = (data.get("student_id_number") or "").strip()
    name       = (data.get("name") or "").strip()
    password   = data.get("password") or ""

    if not email.endswith("@gbox.adnu.edu.ph"):
        return jsonify({"message": "Use your ADNU GBOX email (@gbox.adnu.edu.ph)"}), 400
    if "-" not in student_id:
        return jsonify({"message": "Student ID must contain a dash (e.g. 2024-00001)"}), 400
    if not name:
        return jsonify({"message": "Name is required"}), 400
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    existing = db.session.execute(
        db.text("SELECT COUNT(*) FROM USERS WHERE email=:e"), {"e": email}
    ).scalar()
    if existing > 0:
        return jsonify({"message": "Email already registered. Please log in."}), 400

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    try:
        db.session.execute(db.text("""
            INSERT INTO USERS (id, name, email, password_hash,
                student_id_number, course, year_level, department)
            VALUES (users_seq.NEXTVAL, :name, :email, :pw,
                :sid, :course, :year, :dept)
        """), {
            "name":   name,
            "email":  email,
            "pw":     hashed,
            "sid":    student_id,
            "course": data.get("course"),
            "year":   data.get("year_level"),
            "dept":   data.get("department"),
        })
        db.session.commit()
        return jsonify({"message": "Registered successfully! Please log in."}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data  = request.get_json()
    email = (data.get("email") or "").strip()
    pw    = data.get("password") or ""
    row   = db.session.execute(db.text("""
        SELECT id, name, email, password_hash,
               student_id_number, course, year_level, department, profile_pic
        FROM USERS WHERE email=:e
    """), {"e": email}).fetchone()
    if not row:
        return jsonify({"message": "No account found with that email."}), 404
    if not bcrypt.check_password_hash(str(row[3]), pw):
        return jsonify({"message": "Incorrect password."}), 401
    profile_pic = abs_url(row[8]) if row[8] else None
    return jsonify({
        "user_id":           row[0],
        "name":              row[1],
        "email":             row[2],
        "student_id_number": row[4],
        "course":            row[5],
        "year_level":        row[6],
        "department":        row[7],
        "profile_pic":       profile_pic,
    })

# ── PROFILE PIC ───────────────────────────────────────────────────────────────

@app.route("/api/users/<int:user_id>/profile-pic", methods=["POST"])
def upload_profile_pic(user_id):
    file = request.files.get("profile_pic")
    if not file:
        return jsonify({"message": "No file provided"}), 400
    url = save_image(file)
    if not url:
        return jsonify({"message": "Invalid image file"}), 400
    try:
        db.session.execute(
            db.text("UPDATE USERS SET profile_pic=:url WHERE id=:id"),
            {"url": url, "id": user_id}
        )
        db.session.commit()
        return jsonify({"message": "Profile picture updated", "profile_pic": abs_url(url)})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── PRODUCTS ──────────────────────────────────────────────────────────────────

@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        seller_id = request.args.get("seller_id")
        search    = (request.args.get("search") or "").strip()
        category  = (request.args.get("category") or "").strip()
        tag       = (request.args.get("tag") or "").strip()
        sort      = request.args.get("sort", "newest")

        order_map = {
            "newest":     "p.id DESC",
            "oldest":     "p.id ASC",
            "price_asc":  "p.price ASC",
            "price_desc": "p.price DESC",
            "name_asc":   "p.title ASC",
            "name_desc":  "p.title DESC",
        }
        order = order_map.get(sort, "p.id DESC")

        base = """
            SELECT p.id, p.title, p.description, p.price, p.category,
                   p.status, p.seller_id, p.image_url, u.name,
                   p.tags, p.created_at
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
        """
        params = {}

        if seller_id:
            sql = base + " WHERE p.seller_id=:sid ORDER BY " + order
            params["sid"] = int(seller_id)
        else:
            conds = ["p.status='Available'"]
            if search:
                conds.append("(LOWER(p.title) LIKE :search OR LOWER(p.description) LIKE :search OR LOWER(p.tags) LIKE :search)")
                params["search"] = f"%{search.lower()}%"
            if category:
                conds.append("p.category=:category")
                params["category"] = category
            if tag:
                conds.append("LOWER(p.tags) LIKE :tag")
                params["tag"] = f"%{tag.lower()}%"
            sql = base + " WHERE " + " AND ".join(conds) + " ORDER BY " + order

        rows = db.session.execute(db.text(sql), params)
        result = []
        for r in rows:
            imgs = parse_images(r[7])
            result.append({
                "id":          r[0],
                "title":       r[1],
                "description": r[2],
                "price":       float(r[3]),
                "category":    r[4],
                "status":      r[5],
                "seller_id":   r[6],
                "image_url":   imgs[0] if imgs else None,
                "images":      imgs,
                "seller_name": r[8],
                "tags":        [t.strip() for t in r[9].split(",")] if r[9] else [],
                "created_at":  str(r[10]) if r[10] else None,
            })
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["GET"])
def get_product(pid):
    try:
        r = db.session.execute(db.text("""
            SELECT p.id, p.title, p.description, p.price, p.category,
                   p.status, p.created_at, u.name, p.seller_id, p.image_url, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id=u.id
            WHERE p.id=:id
        """), {"id": pid}).fetchone()
        if not r:
            return jsonify({"message": "Product not found"}), 404
        imgs = parse_images(r[9])
        return jsonify({
            "id":          r[0],
            "title":       r[1],
            "description": r[2],
            "price":       float(r[3]),
            "category":    r[4],
            "status":      r[5],
            "created_at":  str(r[6]) if r[6] else None,
            "seller_name": r[7],
            "seller_id":   r[8],
            "image_url":   imgs[0] if imgs else None,
            "images":      imgs,
            "tags":        [t.strip() for t in r[10].split(",")] if r[10] else [],
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/products", methods=["POST"])
def create_product():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            title       = (request.form.get("title") or "").strip()
            description = (request.form.get("description") or "").strip()
            price_raw   = request.form.get("price", "0")
            category    = (request.form.get("category") or "General").strip()
            seller_id   = request.form.get("user_id", "").strip()
            tags        = (request.form.get("tags") or "").strip()
            files       = request.files.getlist("images") or request.files.getlist("image")
            image_url   = save_images([f for f in files if f.filename]) if files else None
        else:
            data        = request.get_json() or {}
            title       = (data.get("title") or "").strip()
            description = (data.get("description") or "").strip()
            price_raw   = str(data.get("price", "0"))
            category    = (data.get("category") or "General").strip()
            seller_id   = str(data.get("user_id") or "").strip()
            tags        = (data.get("tags") or "").strip()
            image_url   = None

        # Validate
        if not title:
            return jsonify({"message": "Title is required"}), 400
        if not seller_id:
            return jsonify({"message": "Not logged in. Please log in again."}), 400
        try:
            price     = float(price_raw)
            seller_id = int(seller_id)
        except ValueError:
            return jsonify({"message": "Invalid price or user ID"}), 400
        if price <= 0:
            return jsonify({"message": "Price must be greater than 0"}), 400

        # Verify seller exists
        exists = db.session.execute(
            db.text("SELECT COUNT(*) FROM USERS WHERE id=:id"), {"id": seller_id}
        ).scalar()
        if not exists:
            return jsonify({"message": "User not found. Please log out and log in again."}), 400

        new_id = db.session.execute(db.text("SELECT products_seq.NEXTVAL FROM DUAL")).scalar()
        db.session.execute(db.text("""
            INSERT INTO PRODUCTS (id, title, description, price,
                category, seller_id, created_at, status, image_url, tags)
            VALUES (:id, :title, :desc, :price,
                :cat, :sid, SYSDATE, 'Available', :img, :tags)
        """), {
            "id":    new_id,
            "title": title,
            "desc":  description,
            "price": price,
            "cat":   category,
            "sid":   seller_id,
            "img":   image_url,
            "tags":  tags,
        })
        db.session.commit()
        track_price(new_id, price)
        return jsonify({"message": "Product posted successfully!", "id": new_id}), 201

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            user_id     = int(request.form.get("user_id", 0))
            title       = request.form.get("title")
            description = request.form.get("description")
            price       = float(request.form.get("price", 0))
            category    = request.form.get("category")
            tags        = request.form.get("tags", "")
            files       = request.files.getlist("images") or request.files.getlist("image")
            new_img     = save_images([f for f in files if f.filename]) if files else None
        else:
            data        = request.get_json() or {}
            user_id     = int(data.get("user_id", 0))
            title       = data.get("title")
            description = data.get("description")
            price       = float(data.get("price", 0))
            category    = data.get("category")
            tags        = data.get("tags", "")
            new_img     = None

        row = db.session.execute(
            db.text("SELECT seller_id, price FROM PRODUCTS WHERE id=:id"), {"id": pid}
        ).fetchone()
        if not row:
            return jsonify({"message": "Product not found"}), 404
        if int(row[0]) != user_id:
            return jsonify({"message": "Unauthorized"}), 403

        old_price = float(row[1])
        if new_img:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:t, description=:d, price=:p,
                    category=:c, image_url=:img, tags=:tags WHERE id=:id
            """), {"t":title,"d":description,"p":price,"c":category,"img":new_img,"tags":tags,"id":pid})
        else:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:t, description=:d, price=:p,
                    category=:c, tags=:tags WHERE id=:id
            """), {"t":title,"d":description,"p":price,"c":category,"tags":tags,"id":pid})
        db.session.commit()
        if price != old_price:
            track_price(pid, price)
        return jsonify({"message": "Product updated"})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    user_id = request.args.get("user_id")
    try:
        owner = db.session.execute(
            db.text("SELECT seller_id FROM PRODUCTS WHERE id=:id"), {"id": pid}
        ).scalar()
        if not owner or int(owner) != int(user_id):
            return jsonify({"message": "Unauthorized"}), 403
        db.session.execute(db.text("DELETE FROM CART WHERE product_id=:id"), {"id": pid})
        db.session.execute(db.text("DELETE FROM PRICE_HISTORY WHERE product_id=:id"), {"id": pid})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE id=:id"), {"id": pid})
        db.session.commit()
        return jsonify({"message": "Product deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── PRICE HISTORY ─────────────────────────────────────────────────────────────

@app.route("/api/products/<int:pid>/price-history")
def price_history(pid):
    try:
        rows = db.session.execute(db.text("""
            SELECT price, recorded_at FROM PRICE_HISTORY
            WHERE product_id=:pid ORDER BY recorded_at ASC
        """), {"pid": pid})
        return jsonify([{"price": float(r[0]), "date": str(r[1])} for r in rows])
    except Exception:
        return jsonify([])

# ── TAGS ──────────────────────────────────────────────────────────────────────

@app.route("/api/tags")
def get_tags():
    try:
        rows = db.session.execute(db.text(
            "SELECT tags FROM PRODUCTS WHERE tags IS NOT NULL AND status='Available'"
        ))
        tag_set = set()
        for r in rows:
            if r[0]:
                for t in r[0].split(","):
                    t = t.strip()
                    if t:
                        tag_set.add(t)
        return jsonify(sorted(tag_set))
    except Exception:
        return jsonify([])

@app.route("/api/products/compare")
def compare_by_tag():
    tag = (request.args.get("tag") or "").strip()
    if not tag:
        return jsonify([])
    try:
        rows = db.session.execute(db.text("""
            SELECT p.id, p.title, p.price, p.image_url, u.name, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id=u.id
            WHERE LOWER(p.tags) LIKE :tag AND p.status='Available'
            ORDER BY p.price ASC
        """), {"tag": f"%{tag.lower()}%"})
        result = []
        for r in rows:
            imgs = parse_images(r[3])
            result.append({
                "id": r[0], "title": r[1], "price": float(r[2]),
                "image_url": imgs[0] if imgs else None,
                "seller_name": r[4],
                "tags": [t.strip() for t in r[5].split(",")] if r[5] else []
            })
        return jsonify(result)
    except Exception:
        return jsonify([])

# ── CART ──────────────────────────────────────────────────────────────────────

@app.route("/api/cart")
def get_cart():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "user_id required"}), 400
    try:
        rows = db.session.execute(db.text("""
            SELECT c.id, p.id, p.title, p.price, p.category,
                   p.status, p.seller_id, u.name, p.image_url, c.quantity
            FROM CART c
            JOIN PRODUCTS p ON c.product_id=p.id
            JOIN USERS u ON p.seller_id=u.id
            WHERE c.user_id=:uid
        """), {"uid": int(user_id)})
        items = []
        for r in rows:
            imgs = parse_images(r[8])
            items.append({
                "cart_id":     r[0], "id": r[1], "title": r[2],
                "price":       float(r[3]), "category": r[4], "status": r[5],
                "seller_id":   r[6], "seller_name": r[7],
                "image_url":   imgs[0] if imgs else None,
                "images":      imgs, "quantity": r[9] or 1,
            })
        return jsonify(items)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data       = request.get_json()
    user_id    = data.get("user_id")
    product_id = data.get("product_id")
    try:
        owner = db.session.execute(
            db.text("SELECT seller_id FROM PRODUCTS WHERE id=:id"), {"id": product_id}
        ).scalar()
        if owner and int(owner) == int(user_id):
            return jsonify({"message": "You cannot add your own product to cart"}), 400
        existing = db.session.execute(db.text(
            "SELECT COUNT(*) FROM CART WHERE user_id=:u AND product_id=:p"
        ), {"u": user_id, "p": product_id}).scalar()
        if existing > 0:
            return jsonify({"message": "Already in cart"}), 400
        db.session.execute(db.text("""
            INSERT INTO CART (id, user_id, product_id, quantity)
            VALUES (cart_seq.NEXTVAL, :u, :p, 1)
        """), {"u": user_id, "p": product_id})
        db.session.commit()
        buyer = db.session.execute(db.text("SELECT name FROM USERS WHERE id=:id"), {"id": user_id}).scalar()
        title = db.session.execute(db.text("SELECT title FROM PRODUCTS WHERE id=:id"), {"id": product_id}).scalar()
        if owner:
            notify(owner, f"{buyer} added your product '{title}' to their cart!")
        return jsonify({"message": "Added to cart"}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/cart/<int:cid>", methods=["DELETE"])
def remove_cart(cid):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE id=:id"), {"id": cid})
        db.session.commit()
        return jsonify({"message": "Removed"})
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
                db.text("DELETE FROM CART WHERE id=:c AND user_id=:u"),
                {"c": cart_id, "u": user_id}
            )
        if product_id:
            prod = db.session.execute(
                db.text("SELECT seller_id, title FROM PRODUCTS WHERE id=:id"), {"id": product_id}
            ).fetchone()
            if prod:
                buyer = db.session.execute(db.text("SELECT name FROM USERS WHERE id=:id"), {"id": user_id}).scalar()
                notify(prod[0], f"{buyer} placed an order for '{prod[1]}'!")
        db.session.commit()
        return jsonify({"message": "Order placed successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── MESSAGES ──────────────────────────────────────────────────────────────────

@app.route("/api/messages", methods=["POST"])
def send_message():
    data        = request.get_json()
    sender_id   = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    text        = data.get("message_text") or data.get("content") or data.get("message") or ""
    product_id  = data.get("product_id")
    try:
        db.session.execute(db.text("""
            INSERT INTO MESSAGES (id, sender_id, receiver_id, product_id, message, sent_at, is_read)
            VALUES (messages_seq.NEXTVAL, :s, :r, :pid, :msg, SYSDATE, 0)
        """), {"s": sender_id, "r": receiver_id, "pid": product_id, "msg": text})
        db.session.commit()
        sname = db.session.execute(db.text("SELECT name FROM USERS WHERE id=:id"), {"id": sender_id}).scalar()
        notify(receiver_id, f"New message from {sname}")
        return jsonify({"message": "Sent"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages")
def get_messages():
    try:
        s = int(request.args.get("sender_id"))
        r = int(request.args.get("receiver_id"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid IDs"}), 400
    try:
        rows = db.session.execute(db.text("""
            SELECT sender_id, receiver_id, message, sent_at FROM MESSAGES
            WHERE (sender_id=:s AND receiver_id=:r)
               OR (sender_id=:r AND receiver_id=:s)
            ORDER BY sent_at ASC
        """), {"s": s, "r": r})
        return jsonify([{"sender_id":r[0],"receiver_id":r[1],"message_text":r[2],"sent_at":str(r[3])} for r in rows])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/mark-read", methods=["POST"])
def mark_read():
    data = request.get_json()
    try:
        db.session.execute(db.text("""
            UPDATE MESSAGES SET is_read=1
            WHERE receiver_id=:r AND sender_id=:s AND is_read=0
        """), {"r": int(data.get("reader_id")), "s": int(data.get("sender_id"))})
        db.session.commit()
        return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/threads")
def get_threads():
    try:
        uid = int(request.args.get("user_id"))
    except (TypeError, ValueError):
        return jsonify([])
    try:
        rows = db.session.execute(db.text("""
            SELECT DISTINCT
                CASE WHEN m.sender_id=:u1 THEN m.receiver_id ELSE m.sender_id END AS pid,
                u.name
            FROM MESSAGES m
            JOIN USERS u ON u.id = CASE WHEN m.sender_id=:u2 THEN m.receiver_id ELSE m.sender_id END
            WHERE m.sender_id=:u3 OR m.receiver_id=:u4
        """), {"u1":uid,"u2":uid,"u3":uid,"u4":uid})
        threads = []
        for r in rows:
            pid  = r[0]
            last = db.session.execute(db.text("""
                SELECT message, sent_at FROM MESSAGES
                WHERE (sender_id=:u AND receiver_id=:p)
                   OR (sender_id=:p AND receiver_id=:u)
                ORDER BY sent_at DESC FETCH FIRST 1 ROWS ONLY
            """), {"u":uid,"p":pid}).fetchone()
            unread = db.session.execute(db.text("""
                SELECT COUNT(*) FROM MESSAGES
                WHERE sender_id=:p AND receiver_id=:u AND is_read=0
            """), {"u":uid,"p":pid}).scalar()
            threads.append({
                "seller_id":    pid,
                "seller_name":  r[1],
                "last_message": last[0] if last else "",
                "last_time":    str(last[1]) if last else "",
                "unread":       unread > 0,
            })
        return jsonify(threads)
    except Exception as e:
        traceback.print_exc()
        return jsonify([])

@app.route("/api/messages/unread-count")
def unread_count():
    try:
        uid   = int(request.args.get("user_id"))
        count = db.session.execute(db.text(
            "SELECT COUNT(*) FROM MESSAGES WHERE receiver_id=:u AND is_read=0"
        ), {"u": uid}).scalar()
        return jsonify({"count": count})
    except Exception:
        return jsonify({"count": 0})

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@app.route("/api/notifications")
def get_notifications():
    uid = request.args.get("user_id")
    try:
        rows = db.session.execute(db.text("""
            SELECT id, message, is_read, created_at FROM NOTIFICATIONS
            WHERE user_id=:uid ORDER BY created_at DESC FETCH FIRST 30 ROWS ONLY
        """), {"uid": int(uid)})
        return jsonify([{"id":r[0],"message":r[1],"is_read":r[2],"created_at":str(r[3])} for r in rows])
    except Exception:
        return jsonify([])

@app.route("/api/notifications/read", methods=["POST"])
def mark_notifs_read():
    uid = request.get_json().get("user_id")
    try:
        db.session.execute(db.text("UPDATE NOTIFICATIONS SET is_read=1 WHERE user_id=:u"), {"u": uid})
        db.session.commit()
        return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── PAYMENT ───────────────────────────────────────────────────────────────────

@app.route("/api/users/<int:uid>/payment")
def get_payment(uid):
    try:
        r = db.session.execute(db.text("SELECT gcash_number, bank_details FROM USERS WHERE id=:id"), {"id":uid}).fetchone()
        return jsonify({"gcash": r[0] if r else None, "bank": r[1] if r else None})
    except Exception:
        return jsonify({"gcash": None, "bank": None})

@app.route("/api/users/<int:uid>/payment", methods=["PUT"])
def update_payment(uid):
    data = request.get_json()
    try:
        db.session.execute(db.text(
            "UPDATE USERS SET gcash_number=:g, bank_details=:b WHERE id=:id"
        ), {"g": data.get("gcash"), "b": data.get("bank"), "id": uid})
        db.session.commit()
        return jsonify({"message": "Payment details updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

# ── ADMIN ──────────────────────────────────────────────────────────────────────

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    if (request.get_json() or {}).get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"message": "Wrong password"}), 401

@app.route("/api/admin/stats")
def admin_stats():
    try:
        return jsonify({
            "users":      db.session.execute(db.text("SELECT COUNT(*) FROM USERS")).scalar(),
            "products":   db.session.execute(db.text("SELECT COUNT(*) FROM PRODUCTS")).scalar(),
            "messages":   db.session.execute(db.text("SELECT COUNT(*) FROM MESSAGES")).scalar(),
            "cart_items": db.session.execute(db.text("SELECT COUNT(*) FROM CART")).scalar(),
        })
    except Exception:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users")
def admin_users():
    try:
        rows = db.session.execute(db.text(
            "SELECT id,name,email,student_id_number,course,department,year_level FROM USERS ORDER BY id DESC"
        ))
        return jsonify([{"id":r[0],"name":r[1],"email":r[2],"student_id":r[3],"course":r[4],"department":r[5],"year_level":r[6]} for r in rows])
    except Exception:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products")
def admin_products():
    try:
        rows = db.session.execute(db.text("""
            SELECT p.id, p.title, p.price, p.category, p.status,
                   p.created_at, u.name, p.image_url, p.tags
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id=u.id
            ORDER BY p.id DESC
        """))
        result = []
        for r in rows:
            imgs = parse_images(r[7])
            result.append({
                "id":r[0],"title":r[1],"price":float(r[2]),"category":r[3],"status":r[4],
                "created_at":str(r[5]) if r[5] else None,"seller_name":r[6],
                "image_url":imgs[0] if imgs else None,
                "tags":[t.strip() for t in r[8].split(",")] if r[8] else []
            })
        return jsonify(result)
    except Exception:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/messages")
def admin_messages():
    try:
        rows = db.session.execute(db.text("""
            SELECT m.id, m.sender_id, m.receiver_id, m.message,
                   m.sent_at, m.is_read, u1.name, u2.name
            FROM MESSAGES m
            LEFT JOIN USERS u1 ON m.sender_id=u1.id
            LEFT JOIN USERS u2 ON m.receiver_id=u2.id
            ORDER BY m.sent_at DESC FETCH FIRST 200 ROWS ONLY
        """))
        return jsonify([{
            "id":r[0],"sender_id":r[1],"receiver_id":r[2],"message":r[3],
            "sent_at":str(r[4]) if r[4] else None,"is_read":r[5],
            "sender_name":r[6] or str(r[1]),"receiver_name":r[7] or str(r[2])
        } for r in rows])
    except Exception:
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products/<int:pid>", methods=["DELETE"])
def admin_del_product(pid):
    try:
        for tbl in ["CART","PRICE_HISTORY"]:
            db.session.execute(db.text(f"DELETE FROM {tbl} WHERE product_id=:id"), {"id": pid})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE id=:id"), {"id": pid})
        db.session.commit()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
def admin_del_user(uid):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE user_id=:id"), {"id": uid})
        db.session.execute(db.text("DELETE FROM MESSAGES WHERE sender_id=:id OR receiver_id=:id"), {"id": uid})
        db.session.execute(db.text("DELETE FROM NOTIFICATIONS WHERE user_id=:id"), {"id": uid})
        # Delete price history for user's products first
        db.session.execute(db.text("""
            DELETE FROM PRICE_HISTORY WHERE product_id IN (
                SELECT id FROM PRODUCTS WHERE seller_id=:id
            )
        """), {"id": uid})
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE seller_id=:id"), {"id": uid})
        db.session.execute(db.text("DELETE FROM USERS WHERE id=:id"), {"id": uid})
        db.session.commit()
        return jsonify({"message": "User deleted"})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"message": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)