from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import oracledb
import os

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

db      = SQLAlchemy(app)
bcrypt  = Bcrypt(app)

CORS(app, resources={r"/*": {"origins": "*"}})


# ── HELPERS ───────────────────────────────────────────────────────────────────

def save_image(file):
    if not file:
        return None
    filename = f"{os.urandom(8).hex()}_{file.filename.replace(' ', '_')}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return f"/static/uploads/{filename}"


def send_notification(user_id, message):
    try:
        db.session.execute(db.text("""
            INSERT INTO NOTIFICATIONS (id, user_id, message, is_read, created_at)
            VALUES (notif_seq.NEXTVAL, :user_id, :msg, 0, SYSDATE)
        """), {"user_id": user_id, "msg": message})
        db.session.commit()
    except Exception as e:
        print("NOTIFICATION ERROR (non-fatal):", e)
        db.session.rollback()


# ── ROOT ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "Backend running!"


# ── SERVE ADMIN PANEL ─────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
ADMIN_FOLDER = os.path.join(_ROOT, 'admin')
print(f'[ADMIN] Serving from: {ADMIN_FOLDER}')
print(f'[ADMIN] Folder exists: {os.path.isdir(ADMIN_FOLDER)}')

@app.route("/admin")
@app.route("/admin/")
def serve_admin():
    return send_from_directory(ADMIN_FOLDER, 'index.html')

@app.route("/admin/<path:filename>")
def serve_admin_static(filename):
    return send_from_directory(ADMIN_FOLDER, filename)


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data       = request.get_json()
    email      = data.get("email", "")
    student_id = data.get("student_id_number", "")
    ALLOWED_TEST_EMAILS = ["deckertdotado@gbox.adnu.edu.ph"]
    if email not in ALLOWED_TEST_EMAILS and not email.endswith("@gbox.adnu.edu.ph"):
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
        print("REGISTER ERROR:", e)
        return jsonify({"message": "Server error"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    res  = db.session.execute(
        db.text("""SELECT id, name, email, password_hash,
                   student_id_number, course, year_level, department
            FROM USERS WHERE email = :email"""),
        {"email": data.get("email")}
    ).fetchone()
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
        if seller_id:
            result = db.session.execute(db.text("""
                SELECT p.id, p.title, p.description, p.price, p.category,
                       p.status, p.seller_id, p.image_url, u.name AS seller_name
                FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
                WHERE p.seller_id = :seller_id ORDER BY p.id DESC
            """), {"seller_id": int(seller_id)})
        else:
            result = db.session.execute(db.text("""
                SELECT p.id, p.title, p.description, p.price, p.category,
                       p.status, p.seller_id, p.image_url, u.name AS seller_name
                FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
                WHERE p.status = 'Available' ORDER BY p.id DESC
            """))
        products = []
        for row in result:
            image_url = row[7]
            if image_url:
                image_url = f"http://127.0.0.1:5000{image_url}"
            products.append({
                "id": row[0], "title": row[1], "description": row[2],
                "price": float(row[3]), "category": row[4], "status": row[5],
                "seller_id": row[6], "image_url": image_url, "seller_name": row[8]
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
                   p.status, p.created_at, u.name AS seller_name, p.seller_id, p.image_url
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
            WHERE p.id = :id
        """), {"id": product_id}).fetchone()
        if not res:
            return jsonify({"message": "Product not found"}), 404
        image_url = res[9]
        if image_url:
            image_url = f"http://127.0.0.1:5000{image_url}"
        return jsonify({
            "id": res[0], "title": res[1], "description": res[2],
            "price": float(res[3]), "category": res[4], "status": res[5],
            "created_at": str(res[6]) if res[6] else None,
            "seller_name": res[7], "seller_id": res[8], "image_url": image_url
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
            price       = request.form.get("price")
            category    = request.form.get("category", "General")
            seller_id   = request.form.get("user_id")
            image_url   = save_image(request.files.get("image"))
        else:
            data        = request.get_json()
            title       = data.get("title")
            description = data.get("description")
            price       = data.get("price")
            category    = data.get("category", "General")
            seller_id   = data.get("user_id")
            image_url   = None
        db.session.execute(db.text("""
            INSERT INTO PRODUCTS (id, title, description, price,
                category, seller_id, created_at, status, image_url)
            VALUES (products_seq.NEXTVAL, :title, :description, :price,
                :category, :seller_id, SYSDATE, 'Available', :image_url)
        """), {
            "title": title, "description": description, "price": price,
            "category": category, "seller_id": seller_id, "image_url": image_url
        })
        db.session.commit()
        return jsonify({"message": "Product created successfully"}), 201
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
            price       = request.form.get("price")
            category    = request.form.get("category")
            new_image   = save_image(request.files.get("image"))
        else:
            data        = request.get_json()
            user_id     = data.get("user_id")
            title       = data.get("title")
            description = data.get("description")
            price       = data.get("price")
            category    = data.get("category")
            new_image   = None
        owner = db.session.execute(
            db.text("SELECT seller_id FROM PRODUCTS WHERE id = :id"), {"id": product_id}
        ).scalar()
        if not owner or int(owner) != int(user_id):
            return jsonify({"message": "Unauthorized"}), 403
        if new_image:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:title, description=:description,
                    price=:price, category=:category, image_url=:image_url WHERE id=:id
            """), {"title": title, "description": description, "price": price,
                   "category": category, "image_url": new_image, "id": product_id})
        else:
            db.session.execute(db.text("""
                UPDATE PRODUCTS SET title=:title, description=:description,
                    price=:price, category=:category WHERE id=:id
            """), {"title": title, "description": description,
                   "price": price, "category": category, "id": product_id})
        db.session.commit()
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
        db.session.execute(db.text("DELETE FROM PRODUCTS WHERE id = :id"), {"id": product_id})
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"})
    except Exception as e:
        db.session.rollback()
        print("DELETE PRODUCT ERROR:", e)
        return jsonify({"message": "Server error"}), 500


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
            image_url = row[8]
            if image_url:
                image_url = f"http://127.0.0.1:5000{image_url}"
            items.append({
                "cart_id": row[0], "id": row[1], "title": row[2],
                "price": float(row[3]), "category": row[4], "status": row[5],
                "seller_id": row[6], "seller_name": row[7],
                "image_url": image_url, "quantity": row[9] or 1
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
        print("REMOVE CART ERROR:", e)
        return jsonify({"message": "Server error"}), 500


# ── CHECKOUT ──────────────────────────────────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    user_id    = data.get("user_id")
    cart_id    = data.get("cart_id")   # if coming from cart modal (single item)
    product_id = data.get("product_id")
    try:
        if cart_id:
            # Place order for one specific cart item only
            db.session.execute(
                db.text("DELETE FROM CART WHERE id = :cart_id AND user_id = :user_id"),
                {"cart_id": cart_id, "user_id": user_id}
            )
        else:
            # Buy Now flow — no cart row to delete, just record the order
            pass
        db.session.commit()
        return jsonify({"message": "Order placed successfully"})
    except Exception as e:
        db.session.rollback()
        print("CHECKOUT ERROR:", e)
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
        """), {
            "sender": sender_id, "receiver": receiver_id,
            "product_id": product_id, "message": message_text
        })
        db.session.commit()
        sender_name = db.session.execute(
            db.text("SELECT name FROM USERS WHERE id = :id"), {"id": sender_id}
        ).scalar()
        send_notification(receiver_id, f"New message from {sender_name}")
        return jsonify({"message": "Message sent"}), 201
    except Exception as e:
        db.session.rollback()
        print("MESSAGE ERROR:", e)
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
        messages = []
        for row in result:
            messages.append({
                "sender_id":    row[0],
                "receiver_id":  row[1],
                "message_text": row[2],
                "sent_at":      str(row[3])
            })
        return jsonify(messages)
    except Exception as e:
        print("GET MESSAGES ERROR:", e)
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
                "seller_id":    partner_id,
                "seller_name":  row[1],
                "last_message": last[0] if last else "",
                "last_time":    str(last[1]) if last else "",
                "unread":       unread > 0
            })
        return jsonify(threads)
    except Exception as e:
        print("GET THREADS ERROR:", e)
        return jsonify({"message": "Server error"}), 500


@app.route("/api/messages/unread-count", methods=["GET"])
def unread_count():
    try:
        user_id = int(request.args.get("user_id"))
    except (TypeError, ValueError):
        return jsonify({"count": 0})
    try:
        count = db.session.execute(db.text("""
            SELECT COUNT(*) FROM MESSAGES WHERE receiver_id = :uid AND is_read = 0
        """), {"uid": user_id}).scalar()
        return jsonify({"count": count})
    except Exception as e:
        print("UNREAD COUNT ERROR:", e)
        return jsonify({"count": 0})


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")
    try:
        result = db.session.execute(db.text("""
            SELECT id, message, is_read, created_at FROM NOTIFICATIONS
            WHERE user_id = :user_id ORDER BY created_at DESC
            FETCH FIRST 20 ROWS ONLY
        """), {"user_id": int(user_id)})
        notifs = []
        for row in result:
            notifs.append({
                "id": row[0], "message": row[1],
                "is_read": row[2], "created_at": str(row[3])
            })
        return jsonify(notifs)
    except Exception as e:
        print("GET NOTIF ERROR:", e)
        return jsonify([])


@app.route("/api/notifications/read", methods=["POST"])
def mark_notifications_read():
    user_id = request.get_json().get("user_id")
    try:
        db.session.execute(db.text(
            "UPDATE NOTIFICATIONS SET is_read=1 WHERE user_id=:uid"
        ), {"uid": user_id})
        db.session.commit()
        return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error"}), 500


# ── SELLER PAYMENT INFO ───────────────────────────────────────────────────────
# Requires these columns in USERS table (run once in Oracle):
#   ALTER TABLE USERS ADD gcash_number VARCHAR2(20);
#   ALTER TABLE USERS ADD bank_details VARCHAR2(200);

@app.route("/api/users/<int:user_id>/payment", methods=["GET"])
def get_seller_payment(user_id):
    try:
        res = db.session.execute(db.text("""
            SELECT gcash_number, bank_details FROM USERS WHERE id = :id
        """), {"id": user_id}).fetchone()
        if not res:
            return jsonify({"gcash": None, "bank": None})
        return jsonify({
            "gcash": res[0] if res[0] else None,
            "bank":  res[1] if res[1] else None
        })
    except Exception as e:
        print("GET SELLER PAYMENT ERROR:", e)
        # Return nulls gracefully — frontend shows "coordinate with seller via chat"
        return jsonify({"gcash": None, "bank": None})


@app.route("/api/users/<int:user_id>/payment", methods=["PUT"])
def update_seller_payment(user_id):
    """Sellers call this from their Profile page to set their GCash/bank details."""
    data = request.get_json()
    try:
        db.session.execute(db.text("""
            UPDATE USERS SET gcash_number = :gcash, bank_details = :bank WHERE id = :id
        """), {
            "gcash": data.get("gcash"),
            "bank":  data.get("bank"),
            "id":    user_id
        })
        db.session.commit()
        return jsonify({"message": "Payment details updated"})
    except Exception as e:
        db.session.rollback()
        print("UPDATE PAYMENT ERROR:", e)
        return jsonify({"message": "Server error"}), 500


# ── ADMIN ─────────────────────────────────────────────────────────────────────

ADMIN_PASSWORD = "adnu_admin_2024"


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"message": "Wrong password"}), 401


@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    try:
        users    = db.session.execute(db.text("SELECT COUNT(*) FROM USERS")).scalar()
        products = db.session.execute(db.text("SELECT COUNT(*) FROM PRODUCTS")).scalar()
        messages = db.session.execute(db.text("SELECT COUNT(*) FROM MESSAGES")).scalar()
        cart     = db.session.execute(db.text("SELECT COUNT(*) FROM CART")).scalar()
        return jsonify({"users": users, "products": products,
                        "messages": messages, "cart_items": cart})
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
            "id": r[0], "name": r[1], "email": r[2],
            "student_id": r[3], "course": r[4],
            "department": r[5], "year_level": r[6]
        } for r in result])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500


@app.route("/api/admin/products", methods=["GET"])
def admin_products():
    try:
        result = db.session.execute(db.text("""
            SELECT p.id, p.title, p.price, p.category, p.status,
                   p.created_at, u.name AS seller_name, p.image_url
            FROM PRODUCTS p LEFT JOIN USERS u ON p.seller_id = u.id
            ORDER BY p.id DESC
        """))
        return jsonify([{
            "id": r[0], "title": r[1], "price": float(r[2]),
            "category": r[3], "status": r[4],
            "created_at": str(r[5]) if r[5] else None,
            "seller_name": r[6],
            "image_url": f"http://127.0.0.1:5000{r[7]}" if r[7] else None
        } for r in result])
    except Exception as e:
        return jsonify({"message": "Server error"}), 500


@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def admin_delete_product(product_id):
    try:
        db.session.execute(db.text("DELETE FROM CART WHERE product_id = :id"), {"id": product_id})
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
                   m.sent_at, m.is_read,
                   u1.name AS sender_name, u2.name AS receiver_name
            FROM MESSAGES m
            LEFT JOIN USERS u1 ON m.sender_id = u1.id
            LEFT JOIN USERS u2 ON m.receiver_id = u2.id
            ORDER BY m.sent_at DESC
            FETCH FIRST 200 ROWS ONLY
        """))
        return jsonify([{
            "id":            r[0],
            "sender_id":     r[1],
            "receiver_id":   r[2],
            "message":       r[3],
            "sent_at":       str(r[4]) if r[4] else None,
            "is_read":       r[5],
            "sender_name":   r[6] or str(r[1]),
            "receiver_name": r[7] or str(r[2])
        } for r in result])
    except Exception as e:
        print("ADMIN MESSAGES ERROR:", e)
        return jsonify({"message": "Server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)