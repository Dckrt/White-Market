from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os, json, traceback
from datetime import datetime, timedelta

app = Flask(__name__)

# ── DATABASE CONFIG ────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
IS_POSTGRES  = False
IS_ORACLE    = False

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    IS_POSTGRES = True
else:
    try:
        import oracledb
        INSTANT_CLIENT = r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_26"
        if os.path.exists(INSTANT_CLIENT):
            oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT)
        app.config["SQLALCHEMY_DATABASE_URI"] = "oracle+oracledb://dotado:202400926@localhost:1521/?service_name=XE"
        IS_ORACLE = True
        print("✅ Using Oracle (local dev)")
    except Exception as e:
        print(f"Oracle not available: {e}")
        fallback = os.path.join(os.path.dirname(__file__), "fallback.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{fallback}"
        IS_POSTGRES = True
        print(f"⚠️  No DB configured — falling back to SQLite at {fallback}")

app.config["SECRET_KEY"]                     = os.environ.get("SECRET_KEY", "whitemarket_secret_2024")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"]             = 20 * 1024 * 1024
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "adnu_admin_2024")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── SQL HELPERS ────────────────────────────────────────────────────────────
LIMIT1   = "LIMIT 1"   if not IS_ORACLE else "FETCH FIRST 1 ROWS ONLY"
LIMIT10  = "LIMIT 10"  if not IS_ORACLE else "FETCH FIRST 10 ROWS ONLY"
LIMIT30  = "LIMIT 30"  if not IS_ORACLE else "FETCH FIRST 30 ROWS ONLY"
LIMIT100 = "LIMIT 100" if not IS_ORACLE else "FETCH FIRST 100 ROWS ONLY"
LIMIT200 = "LIMIT 200" if not IS_ORACLE else "FETCH FIRST 200 ROWS ONLY"
NOW_SQL  = "NOW()"     if not IS_ORACLE else "SYSDATE"

def T(name):
    return name.lower() if not IS_ORACLE else name.upper()

# ── INIT TABLES ────────────────────────────────────────────────────────────
def init_postgres():
    if IS_ORACLE:
        return
    stmts = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            student_id_number VARCHAR(50),
            course VARCHAR(200),
            year_level VARCHAR(20),
            department VARCHAR(200),
            profile_pic VARCHAR(500),
            gcash_number VARCHAR(20),
            bank_details VARCHAR(200),
            google_id VARCHAR(100),
            is_admin INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            block_until TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            student_id_number VARCHAR(50),
            course VARCHAR(200),
            year_level VARCHAR(20),
            department VARCHAR(200),
            profile_pic VARCHAR(500),
            gcash_number VARCHAR(20),
            bank_details VARCHAR(200),
            google_id VARCHAR(100),
            is_admin INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            block_until TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description VARCHAR(2000),
            price NUMERIC(10,2) NOT NULL,
            category VARCHAR(100) DEFAULT 'General',
            status VARCHAR(50) DEFAULT 'Available',
            seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            image_url TEXT,
            tags VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description VARCHAR(2000),
            price NUMERIC(10,2) NOT NULL,
            category VARCHAR(100) DEFAULT 'General',
            status VARCHAR(50) DEFAULT 'Available',
            seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            image_url TEXT,
            tags VARCHAR(500),
            created_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            price NUMERIC(10,2) NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS price_history (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            price NUMERIC(10,2) NOT NULL,
            recorded_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id)
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, product_id)
        )""",
        """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            product_title VARCHAR(200) NOT NULL,
            product_price NUMERIC(10,2) NOT NULL,
            product_image VARCHAR(500),
            payment_method VARCHAR(50) DEFAULT 'Cash',
            pickup_location VARCHAR(200),
            status VARCHAR(50) DEFAULT 'Pending',
            ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            product_title VARCHAR(200) NOT NULL,
            product_price NUMERIC(10,2) NOT NULL,
            product_image VARCHAR(500),
            payment_method VARCHAR(50) DEFAULT 'Cash',
            pickup_location VARCHAR(200),
            status VARCHAR(50) DEFAULT 'Pending',
            ordered_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            receiver_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            message VARCHAR(4000) NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            receiver_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            message VARCHAR(4000) NOT NULL,
            sent_at TIMESTAMP DEFAULT NOW(),
            is_read INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            message VARCHAR(500) NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""" if not IS_POSTGRES else """CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            message VARCHAR(500) NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        )""",
    ]
    pg_only = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS block_until TIMESTAMP",
    ]
    for s in stmts:
        try: db.session.execute(db.text(s))
        except Exception as e: print(f"Init table error: {e}")
    if IS_POSTGRES:
        for s in pg_only:
            try: db.session.execute(db.text(s))
            except Exception as e: print(f"Init column error: {e}")
    db.session.commit()
    print("✅ PostgreSQL/SQLite tables ready")

def init_oracle():
    if not IS_ORACLE: return
    existing = set()
    try:
        rows = db.session.execute(db.text(
            "SELECT column_name FROM user_tab_columns WHERE table_name='USERS'"
        )).fetchall()
        existing = {r[0].upper() for r in rows}
    except Exception as e:
        print(f"Oracle column check error: {e}")
    additions = {
        "IS_ADMIN":    "ALTER TABLE USERS ADD (is_admin NUMBER(1) DEFAULT 0)",
        "IS_BLOCKED":  "ALTER TABLE USERS ADD (is_blocked NUMBER(1) DEFAULT 0)",
        "BLOCK_UNTIL": "ALTER TABLE USERS ADD (block_until DATE)",
    }
    for col, sql in additions.items():
        if col not in existing:
            try: db.session.execute(db.text(sql)); db.session.commit(); print(f"✅ Oracle: added {col}")
            except Exception as e: print(f"Oracle add {col} error: {e}"); db.session.rollback()
    print("✅ Oracle columns checked")

with app.app_context():
    init_postgres()
    init_oracle()

# ── HELPERS ────────────────────────────────────────────────────────────────
def save_image(file):
    if not file or not getattr(file, 'filename', None) or file.filename == '': return None
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']: return None
    filename = f"{os.urandom(8).hex()}{ext}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return f"/static/uploads/{filename}"

def save_images(files):
    urls = [u for u in (save_image(f) for f in files) if u]
    return json.dumps(urls) if urls else None

def abs_url(path):
    if not path: return None
    if path.startswith("http"): return path
    host  = request.headers.get('X-Forwarded-Host', request.host)
    proto = request.headers.get('X-Forwarded-Proto', 'http')
    return f"{proto}://{host}{path}"

def parse_images(raw):
    if not raw: return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list): return [abs_url(u) for u in parsed if u]
        return [abs_url(raw)]
    except: return [abs_url(raw)]

def notify(user_id, message):
    try:
        N = T('notifications')
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {N} (id,user_id,message,is_read,created_at) VALUES (notif_seq.NEXTVAL,:uid,:msg,0,SYSDATE)"), {"uid": user_id, "msg": message})
        else:
            db.session.execute(db.text(f"INSERT INTO {N} (user_id,message,is_read) VALUES (:uid,:msg,0)"), {"uid": user_id, "msg": message})
        db.session.commit()
    except Exception as e:
        print("NOTIFY ERROR:", e); db.session.rollback()

def track_price(product_id, price):
    try:
        PH = T('price_history')
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {PH} (id,product_id,price,recorded_at) VALUES (price_hist_seq.NEXTVAL,:pid,:p,SYSDATE)"), {"pid": product_id, "p": price})
        else:
            db.session.execute(db.text(f"INSERT INTO {PH} (product_id,price) VALUES (:pid,:p)"), {"pid": product_id, "p": price})
        db.session.commit()
    except: db.session.rollback()

def insert_product(title, description, price, category, seller_id, image_url, tags):
    P = T('products')
    if IS_ORACLE:
        new_id = db.session.execute(db.text("SELECT products_seq.NEXTVAL FROM DUAL")).scalar()
        db.session.execute(db.text(f"INSERT INTO {P} (id,title,description,price,category,seller_id,created_at,status,image_url,tags) VALUES (:id,:t,:d,:p,:c,:sid,SYSDATE,'Available',:img,:tags)"),
                           {"id": new_id, "t": title, "d": description, "p": price, "c": category, "sid": seller_id, "img": image_url, "tags": tags})
        return new_id
    elif IS_POSTGRES:
        res = db.session.execute(db.text(f"INSERT INTO {P} (title,description,price,category,seller_id,status,image_url,tags) VALUES (:t,:d,:p,:c,:sid,'Available',:img,:tags) RETURNING id"),
                                 {"t": title, "d": description, "p": price, "c": category, "sid": seller_id, "img": image_url, "tags": tags})
        return res.fetchone()[0]
    else:
        db.session.execute(db.text(f"INSERT INTO {P} (title,description,price,category,seller_id,status,image_url,tags) VALUES (:t,:d,:p,:c,:sid,'Available',:img,:tags)"),
                           {"t": title, "d": description, "p": price, "c": category, "sid": seller_id, "img": image_url, "tags": tags})
        return db.session.execute(db.text("SELECT last_insert_rowid()")).scalar()

def get_user_is_admin(user_id):
    try:
        row = db.session.execute(db.text(f"SELECT is_admin FROM {T('users')} WHERE id=:id"), {"id": user_id}).fetchone()
        return row and int(row[0] or 0) == 1
    except: return False

# ── ROOT ───────────────────────────────────────────────────────────────────
@app.route("/")
def home(): return "AdnuMarket API ✅"

@app.route("/static/uploads/<path:filename>")
def serve_upload(filename): return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ── STATS ──────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def public_stats():
    try:
        return jsonify({
            "users":    db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('users')}")).scalar(),
            "products": db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('products')} WHERE status='Available'")).scalar(),
            "colleges": 6
        })
    except: return jsonify({"users": 0, "products": 0, "colleges": 6})

# ── AUTH ───────────────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = (data.get("email") or "").strip()
    sid   = (data.get("student_id_number") or "").strip()
    name  = (data.get("name") or "").strip()
    pw    = data.get("password") or ""
    if not email.endswith("@gbox.adnu.edu.ph"): return jsonify({"message": "Use your ADNU GBOX email (@gbox.adnu.edu.ph)"}), 400
    if "-" not in sid: return jsonify({"message": "Student ID must contain a dash (e.g. 2024-00001)"}), 400
    if not name: return jsonify({"message": "Name is required"}), 400
    if len(pw) < 6: return jsonify({"message": "Password must be at least 6 characters"}), 400
    UN = T('users')
    if db.session.execute(db.text(f"SELECT COUNT(*) FROM {UN} WHERE email=:e"), {"e": email}).scalar() > 0:
        return jsonify({"message": "Email already registered. Please log in."}), 400
    hashed = bcrypt.generate_password_hash(pw).decode("utf-8")
    try:
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {UN} (id,name,email,password_hash,student_id_number,course,year_level,department) VALUES (users_seq.NEXTVAL,:name,:email,:pw,:sid,:course,:year,:dept)"),
                               {"name": name, "email": email, "pw": hashed, "sid": sid, "course": data.get("course"), "year": data.get("year_level"), "dept": data.get("department")})
        else:
            db.session.execute(db.text(f"INSERT INTO {UN} (name,email,password_hash,student_id_number,course,year_level,department,is_admin) VALUES (:name,:email,:pw,:sid,:course,:year,:dept,0)"),
                               {"name": name, "email": email, "pw": hashed, "sid": sid, "course": data.get("course"), "year": data.get("year_level"), "dept": data.get("department")})
        db.session.commit()
        return jsonify({"message": "Registered successfully! Please log in."}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data  = request.get_json()
    email = (data.get("email") or "").strip()
    pw    = data.get("password") or ""
    UN = T('users')
    row = db.session.execute(db.text(f"SELECT id,name,email,student_id_number,course,year_level,department,profile_pic,password_hash,is_admin,is_blocked,block_until FROM {UN} WHERE email=:e"), {"e": email}).fetchone()
    if not row: return jsonify({"message": "No account found with that email."}), 404
    if not row[8]: return jsonify({"message": "This account uses Google Sign-In."}), 400
    if not bcrypt.check_password_hash(str(row[8]), pw): return jsonify({"message": "Incorrect password."}), 401
    is_blocked = int(row[10] or 0); block_until = row[11]
    if is_blocked:
        if block_until is None: return jsonify({"message": "Your account has been permanently suspended. Contact admin."}), 403
        elif datetime.now() < block_until:
            return jsonify({"message": f"Your account is temporarily suspended until {block_until.strftime('%B %d, %Y %I:%M %p')}."}), 403
        else:
            db.session.execute(db.text(f"UPDATE {UN} SET is_blocked=0, block_until=NULL WHERE id=:id"), {"id": row[0]}); db.session.commit()
    return jsonify({"user_id": row[0], "name": row[1], "email": row[2], "student_id_number": row[3], "course": row[4], "year_level": row[5], "department": row[6], "profile_pic": abs_url(row[7]) if row[7] else None, "is_admin": int(row[9] or 0)})

@app.route("/api/users/<int:uid>/profile-pic", methods=["POST"])
def upload_profile_pic(uid):
    file = request.files.get("profile_pic")
    if not file: return jsonify({"message": "No file provided"}), 400
    url = save_image(file)
    if not url: return jsonify({"message": "Invalid image file"}), 400
    try:
        db.session.execute(db.text(f"UPDATE {T('users')} SET profile_pic=:url WHERE id=:id"), {"url": url, "id": uid}); db.session.commit()
        return jsonify({"message": "Updated", "profile_pic": abs_url(url)})
    except: db.session.rollback(); return jsonify({"message": "Server error"}), 500

# ── PRODUCTS ───────────────────────────────────────────────────────────────
@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        seller_id = request.args.get("seller_id"); search = (request.args.get("search") or "").strip()
        category  = (request.args.get("category") or "").strip(); tag = (request.args.get("tag") or "").strip()
        sort = request.args.get("sort", "newest")
        order = {"newest":"p.id DESC","oldest":"p.id ASC","price_asc":"p.price ASC","price_desc":"p.price DESC","name_asc":"p.title ASC","name_desc":"p.title DESC"}.get(sort, "p.id DESC")
        P, UN = T('products'), T('users')
        base = f"SELECT p.id,p.title,p.description,p.price,p.category,p.status,p.seller_id,p.image_url,u.name,p.tags,p.created_at FROM {P} p LEFT JOIN {UN} u ON p.seller_id=u.id"
        params = {}
        if seller_id:
            sql = base + f" WHERE p.seller_id=:sid ORDER BY {order}"; params["sid"] = int(seller_id)
        else:
            conds = ["p.status='Available'"]
            if search: conds.append("(LOWER(p.title) LIKE :search OR LOWER(p.description) LIKE :search OR LOWER(p.tags) LIKE :search)"); params["search"] = f"%{search.lower()}%"
            if category: conds.append("p.category=:category"); params["category"] = category
            if tag: conds.append("LOWER(p.tags) LIKE :tag"); params["tag"] = f"%{tag.lower()}%"
            sql = base + " WHERE " + " AND ".join(conds) + f" ORDER BY {order}"
        result = []
        for r in db.session.execute(db.text(sql), params):
            imgs = parse_images(r[7])
            result.append({"id": r[0], "title": r[1], "description": r[2], "price": float(r[3]), "category": r[4], "status": r[5], "seller_id": r[6], "image_url": imgs[0] if imgs else None, "images": imgs, "seller_name": r[8], "tags": [t.strip() for t in r[9].split(",")] if r[9] else [], "created_at": str(r[10]) if r[10] else None})
        return jsonify(result)
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["GET"])
def get_product(pid):
    try:
        P, UN = T('products'), T('users')
        r = db.session.execute(db.text(f"SELECT p.id,p.title,p.description,p.price,p.category,p.status,p.created_at,u.name,p.seller_id,p.image_url,p.tags FROM {P} p LEFT JOIN {UN} u ON p.seller_id=u.id WHERE p.id=:id"), {"id": pid}).fetchone()
        if not r: return jsonify({"message": "Product not found"}), 404
        imgs = parse_images(r[9])
        return jsonify({"id": r[0], "title": r[1], "description": r[2], "price": float(r[3]), "category": r[4], "status": r[5], "created_at": str(r[6]) if r[6] else None, "seller_name": r[7], "seller_id": r[8], "image_url": imgs[0] if imgs else None, "images": imgs, "tags": [t.strip() for t in r[10].split(",")] if r[10] else []})
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/products", methods=["POST"])
def create_product():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            title = (request.form.get("title") or "").strip(); description = (request.form.get("description") or "").strip()
            price_raw = request.form.get("price", "0"); category = (request.form.get("category") or "General").strip()
            seller_id = request.form.get("user_id", "").strip(); tags = (request.form.get("tags") or "").strip()
            files = request.files.getlist("images") or request.files.getlist("image")
            image_url = save_images([f for f in files if f.filename]) if files else None
        else:
            data = request.get_json() or {}
            title = (data.get("title") or "").strip(); description = (data.get("description") or "").strip()
            price_raw = str(data.get("price", "0")); category = (data.get("category") or "General").strip()
            seller_id = str(data.get("user_id") or "").strip(); tags = (data.get("tags") or "").strip(); image_url = None
        if not title: return jsonify({"message": "Title is required"}), 400
        if not seller_id: return jsonify({"message": "Not logged in"}), 400
        try: price = float(price_raw); seller_id = int(seller_id)
        except: return jsonify({"message": "Invalid price or user ID"}), 400
        if price <= 0: return jsonify({"message": "Price must be > 0"}), 400
        if not db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('users')} WHERE id=:id"), {"id": seller_id}).scalar():
            return jsonify({"message": "User not found. Please log out and log in again."}), 400
        new_id = insert_product(title, description, price, category, seller_id, image_url, tags)
        db.session.commit(); track_price(new_id, price)
        return jsonify({"message": "Product posted successfully!", "id": new_id}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            user_id = int(request.form.get("user_id", 0)); title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip(); price = float(request.form.get("price", 0))
            category = request.form.get("category", "").strip(); status = request.form.get("status", "Available").strip()
            tags = (request.form.get("tags") or "").strip()
            files = request.files.getlist("images") or request.files.getlist("image")
            new_img = save_images([f for f in files if f.filename]) if files else None
        else:
            data = request.get_json() or {}; user_id = int(data.get("user_id", 0))
            title = (data.get("title") or "").strip(); description = (data.get("description") or "").strip()
            price = float(data.get("price", 0)); category = (data.get("category") or "").strip()
            status = (data.get("status") or "Available").strip(); tags = (data.get("tags") or "").strip(); new_img = None
        P = T('products')
        row = db.session.execute(db.text(f"SELECT seller_id,price FROM {P} WHERE id=:id"), {"id": pid}).fetchone()
        if not row: return jsonify({"message": "Product not found"}), 404
        if int(row[0]) != user_id and not get_user_is_admin(user_id): return jsonify({"message": "Unauthorized"}), 403
        old_price = float(row[1])
        if new_img:
            db.session.execute(db.text(f"UPDATE {P} SET title=:t,description=:d,price=:p,category=:c,status=:s,image_url=:img,tags=:tags WHERE id=:id"),
                               {"t": title, "d": description, "p": price, "c": category, "s": status, "img": new_img, "tags": tags, "id": pid})
        else:
            db.session.execute(db.text(f"UPDATE {P} SET title=:t,description=:d,price=:p,category=:c,status=:s,tags=:tags WHERE id=:id"),
                               {"t": title, "d": description, "p": price, "c": category, "s": status, "tags": tags, "id": pid})
        db.session.commit()
        if price != old_price: track_price(pid, price)
        return jsonify({"message": "Product updated"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    user_id = request.args.get("user_id")
    try:
        P = T('products')
        row = db.session.execute(db.text(f"SELECT seller_id FROM {P} WHERE id=:id"), {"id": pid}).fetchone()
        if not row: return jsonify({"message": "Product not found"}), 404
        if int(row[0]) != int(user_id) and not get_user_is_admin(int(user_id)): return jsonify({"message": "Unauthorized"}), 403
        for tbl in [T('cart'), T('price_history')]:
            db.session.execute(db.text(f"DELETE FROM {tbl} WHERE product_id=:id"), {"id": pid})
        db.session.execute(db.text(f"DELETE FROM {P} WHERE id=:id"), {"id": pid}); db.session.commit()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

@app.route("/api/products/<int:pid>/price-history")
def price_history(pid):
    try:
        rows = db.session.execute(db.text(f"SELECT price,recorded_at FROM {T('price_history')} WHERE product_id=:pid ORDER BY recorded_at ASC"), {"pid": pid})
        return jsonify([{"price": float(r[0]), "date": str(r[1])} for r in rows])
    except: return jsonify([])

@app.route("/api/tags")
def get_tags():
    try:
        rows = db.session.execute(db.text(f"SELECT tags FROM {T('products')} WHERE tags IS NOT NULL AND status='Available'"))
        tag_set = set()
        for r in rows:
            if r[0]:
                for t in r[0].split(","):
                    t = t.strip()
                    if t: tag_set.add(t)
        return jsonify(sorted(tag_set))
    except: return jsonify([])

@app.route("/api/products/compare")
def compare_by_tag():
    tag = (request.args.get("tag") or "").strip()
    if not tag: return jsonify([])
    try:
        P, UN = T('products'), T('users')
        rows = db.session.execute(db.text(f"SELECT p.id,p.title,p.price,p.image_url,u.name,p.tags FROM {P} p LEFT JOIN {UN} u ON p.seller_id=u.id WHERE LOWER(p.tags) LIKE :tag AND p.status='Available' ORDER BY p.price ASC"), {"tag": f"%{tag.lower()}%"})
        result = []
        for r in rows:
            imgs = parse_images(r[3])
            result.append({"id": r[0], "title": r[1], "price": float(r[2]), "image_url": imgs[0] if imgs else None, "seller_name": r[4], "tags": [t.strip() for t in r[5].split(",")] if r[5] else []})
        return jsonify(result)
    except: return jsonify([])

# ── REVIEWS ────────────────────────────────────────────────────────────────
@app.route('/api/reviews', methods=['POST'])
def add_review():
    try:
        data = request.json; reviewer_id = data.get('reviewer_id'); seller_id = data.get('seller_id')
        rating = data.get('rating'); comment_text = data.get('comment_text', '')
        existing = db.session.execute(db.text("SELECT COUNT(*) FROM REVIEWS WHERE REVIEWER_ID=:rid AND SELLER_ID=:sid"), {"rid": reviewer_id, "sid": seller_id}).scalar()
        if existing and int(existing) > 0: return jsonify({'success': False, 'message': 'You already reviewed this seller'}), 400
        db.session.execute(db.text("INSERT INTO REVIEWS (REVIEWER_ID,SELLER_ID,RATING,COMMENT_TEXT) VALUES (:rid,:sid,:rating,:comment)"), {"rid": reviewer_id, "sid": seller_id, "rating": rating, "comment": comment_text})
        notify(seller_id, f"You received a new {rating}-star review ⭐")
        db.session.commit()
        return jsonify({'success': True, 'message': 'Review submitted successfully'})
    except Exception as e:
        db.session.rollback(); return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sellers/<int:seller_id>/rating')
def get_seller_rating(seller_id):
    row = db.session.execute(db.text("SELECT ROUND(AVG(RATING),1), COUNT(*) FROM REVIEWS WHERE SELLER_ID=:sid"), {"sid": seller_id}).fetchone()
    return jsonify({'avg_rating': float(row[0]) if row[0] else 0, 'total_reviews': row[1]})

# ── CART ───────────────────────────────────────────────────────────────────
@app.route("/api/cart")
def get_cart():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"message": "user_id required"}), 400
    try:
        C, P, UN = T('cart'), T('products'), T('users')
        rows = db.session.execute(db.text(f"SELECT c.id,p.id,p.title,p.price,p.category,p.status,p.seller_id,u.name,p.image_url,c.quantity FROM {C} c JOIN {P} p ON c.product_id=p.id JOIN {UN} u ON p.seller_id=u.id WHERE c.user_id=:uid"), {"uid": int(user_id)})
        items = []
        for r in rows:
            imgs = parse_images(r[8])
            items.append({"cart_id": r[0], "id": r[1], "title": r[2], "price": float(r[3]), "category": r[4], "status": r[5], "seller_id": r[6], "seller_name": r[7], "image_url": imgs[0] if imgs else None, "images": imgs, "quantity": r[9] or 1})
        return jsonify(items)
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json(); user_id = data.get("user_id"); product_id = data.get("product_id")
    try:
        P, C, UN = T('products'), T('cart'), T('users')
        owner = db.session.execute(db.text(f"SELECT seller_id FROM {P} WHERE id=:id"), {"id": product_id}).scalar()
        if owner and int(owner) == int(user_id): return jsonify({"message": "You cannot add your own product to cart"}), 400
        if db.session.execute(db.text(f"SELECT COUNT(*) FROM {C} WHERE user_id=:u AND product_id=:p"), {"u": user_id, "p": product_id}).scalar() > 0:
            return jsonify({"message": "Already in cart"}), 400
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {C} (id,user_id,product_id,quantity) VALUES (cart_seq.NEXTVAL,:u,:p,1)"), {"u": user_id, "p": product_id})
        else:
            db.session.execute(db.text(f"INSERT INTO {C} (user_id,product_id,quantity) VALUES (:u,:p,1)"), {"u": user_id, "p": product_id})
        db.session.commit()
        buyer = db.session.execute(db.text(f"SELECT name FROM {UN} WHERE id=:id"), {"id": user_id}).scalar()
        title = db.session.execute(db.text(f"SELECT title FROM {P} WHERE id=:id"), {"id": product_id}).scalar()
        if owner: notify(owner, f"{buyer} added your product '{title}' to their cart!")
        return jsonify({"message": "Added to cart"}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/cart/<int:cid>", methods=["DELETE"])
def remove_cart(cid):
    try:
        db.session.execute(db.text(f"DELETE FROM {T('cart')} WHERE id=:id"), {"id": cid}); db.session.commit()
        return jsonify({"message": "Removed"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

# ── CHECKOUT ───────────────────────────────────────────────────────────────
@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json(); buyer_id = data.get("user_id"); cart_id = data.get("cart_id")
    product_id = data.get("product_id"); payment = data.get("payment", "Cash"); location = data.get("location", "")
    try:
        P, O, C, UN = T('products'), T('orders'), T('cart'), T('users')
        prod = db.session.execute(db.text(f"SELECT seller_id,title,price,image_url FROM {P} WHERE id=:id"), {"id": product_id}).fetchone()
        if not prod: return jsonify({"message": "Product not found"}), 404
        seller_id = prod[0]; prod_title = prod[1]; prod_price = float(prod[2])
        imgs = parse_images(prod[3]); prod_image = imgs[0] if imgs else None
        if IS_ORACLE:
            order_id = db.session.execute(db.text("SELECT orders_seq.NEXTVAL FROM DUAL")).scalar()
            db.session.execute(db.text(f"INSERT INTO {O} (id,buyer_id,seller_id,product_id,product_title,product_price,product_image,payment_method,pickup_location,status,ordered_at) VALUES (:id,:buyer,:seller,:pid,:title,:price,:img,:payment,:loc,'Pending',SYSDATE)"),
                               {"id": order_id, "buyer": buyer_id, "seller": seller_id, "pid": product_id, "title": prod_title, "price": prod_price, "img": prod_image, "payment": payment, "loc": location})
        elif IS_POSTGRES:
            res = db.session.execute(db.text(f"INSERT INTO {O} (buyer_id,seller_id,product_id,product_title,product_price,product_image,payment_method,pickup_location,status) VALUES (:buyer,:seller,:pid,:title,:price,:img,:payment,:loc,'Pending') RETURNING id"),
                                     {"buyer": buyer_id, "seller": seller_id, "pid": product_id, "title": prod_title, "price": prod_price, "img": prod_image, "payment": payment, "loc": location})
            order_id = res.fetchone()[0]
        else:
            db.session.execute(db.text(f"INSERT INTO {O} (buyer_id,seller_id,product_id,product_title,product_price,product_image,payment_method,pickup_location,status) VALUES (:buyer,:seller,:pid,:title,:price,:img,:payment,:loc,'Pending')"),
                               {"buyer": buyer_id, "seller": seller_id, "pid": product_id, "title": prod_title, "price": prod_price, "img": prod_image, "payment": payment, "loc": location})
            order_id = db.session.execute(db.text("SELECT last_insert_rowid()")).scalar()
        if cart_id: db.session.execute(db.text(f"DELETE FROM {C} WHERE id=:c AND user_id=:u"), {"c": cart_id, "u": buyer_id})
        db.session.execute(db.text(f"UPDATE {P} SET status='Reserved' WHERE id=:id"), {"id": product_id})
        buyer_name = db.session.execute(db.text(f"SELECT name FROM {UN} WHERE id=:id"), {"id": buyer_id}).scalar()
        notify(seller_id, f"🎉 {buyer_name} placed an order for '{prod_title}'! Meet at: {location}")
        notify(buyer_id,  f"✅ Your order for '{prod_title}' has been placed! Meet seller at: {location}")
        db.session.commit()
        return jsonify({"message": "Order placed successfully", "order_id": order_id})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

# ── ORDERS ─────────────────────────────────────────────────────────────────
@app.route("/api/orders")
def get_orders():
    buyer_id = request.args.get("buyer_id")
    if not buyer_id: return jsonify({"message": "buyer_id required"}), 400
    try:
        O, UN = T('orders'), T('users')
        rows = db.session.execute(db.text(f"SELECT o.id,o.product_id,o.product_title,o.product_price,o.product_image,o.payment_method,o.pickup_location,o.status,o.ordered_at,u.name,o.seller_id FROM {O} o LEFT JOIN {UN} u ON o.seller_id=u.id WHERE o.buyer_id=:bid ORDER BY o.ordered_at DESC"), {"bid": int(buyer_id)})
        result = []
        for r in rows:
            reviewed = False
            try:
                reviewed = db.session.execute(db.text("SELECT COUNT(*) FROM REVIEWS WHERE REVIEWER_ID=:rid AND SELLER_ID=:sid"), {"rid": int(buyer_id), "sid": r[10]}).scalar() > 0
            except: pass
            result.append({"id": r[0], "product_id": r[1], "product_title": r[2], "product_price": float(r[3]), "product_image": abs_url(r[4]) if r[4] else None, "payment_method": r[5], "pickup_location": r[6], "status": r[7], "ordered_at": str(r[8]) if r[8] else None, "seller_name": r[9], "seller_id": r[10], "reviewed": reviewed})
        return jsonify(result)
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/orders/seller")
def get_seller_orders():
    seller_id = request.args.get("seller_id")
    if not seller_id: return jsonify({"message": "seller_id required"}), 400
    try:
        O, UN = T('orders'), T('users')
        rows = db.session.execute(db.text(f"SELECT o.id,o.product_id,o.product_title,o.product_price,o.product_image,o.payment_method,o.pickup_location,o.status,o.ordered_at,u.name FROM {O} o LEFT JOIN {UN} u ON o.buyer_id=u.id WHERE o.seller_id=:sid ORDER BY o.ordered_at DESC"), {"sid": int(seller_id)})
        return jsonify([{"id": r[0], "product_id": r[1], "product_title": r[2], "product_price": float(r[3]), "product_image": abs_url(r[4]) if r[4] else None, "payment_method": r[5], "pickup_location": r[6], "status": r[7], "ordered_at": str(r[8]) if r[8] else None, "buyer_name": r[9]} for r in rows])
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/orders/<int:oid>/status", methods=["PUT"])
def update_order_status(oid):
    data = request.get_json() or {}; status = data.get("status", "Pending")
    if status not in ["Pending", "Completed", "Cancelled"]:
        return jsonify({"message": "Invalid status"}), 400
    try:
        O = T('orders')
        order = db.session.execute(db.text(f"SELECT buyer_id,seller_id,product_title FROM {O} WHERE id=:id"), {"id": oid}).fetchone()
        db.session.execute(db.text(f"UPDATE {O} SET status=:s WHERE id=:id"), {"s": status, "id": oid})
        db.session.commit()
        if order:
            if status == "Completed":
                notify(order[0], f"✅ Your order for '{order[2]}' has been marked as Completed.")
                notify(order[1], f"✅ Order for '{order[2]}' marked as Completed.")
            elif status == "Cancelled":
                notify(order[0], f"❌ Your order for '{order[2]}' was Cancelled.")
                notify(order[1], f"❌ Order for '{order[2]}' was Cancelled.")
        return jsonify({"message": "Status updated"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": "Server error"}), 500

# ── MESSAGES ───────────────────────────────────────────────────────────────
@app.route("/api/messages", methods=["POST"])
def send_message():
    data = request.get_json(); sender_id = int(data.get("sender_id")); receiver_id = int(data.get("receiver_id"))
    text = data.get("message_text") or data.get("content") or data.get("message") or ""; product_id = data.get("product_id")
    try:
        M, UN = T('messages'), T('users')
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {M} (id,sender_id,receiver_id,product_id,message,sent_at,is_read) VALUES (messages_seq.NEXTVAL,:s,:r,:pid,:msg,SYSDATE,0)"), {"s": sender_id, "r": receiver_id, "pid": product_id, "msg": text})
        else:
            db.session.execute(db.text(f"INSERT INTO {M} (sender_id,receiver_id,product_id,message,is_read) VALUES (:s,:r,:pid,:msg,0)"), {"s": sender_id, "r": receiver_id, "pid": product_id, "msg": text})
        db.session.commit()
        sname = db.session.execute(db.text(f"SELECT name FROM {UN} WHERE id=:id"), {"id": sender_id}).scalar()
        notify(receiver_id, f"💬 New message from {sname}")
        return jsonify({"message": "Sent"}), 201
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

@app.route("/api/messages")
def get_messages():
    try:
        s = int(request.args.get("sender_id")); r = int(request.args.get("receiver_id"))
    except: return jsonify({"message": "Invalid IDs"}), 400
    try:
        M = T('messages')
        rows = db.session.execute(db.text(f"SELECT id,sender_id,receiver_id,message,sent_at FROM {M} WHERE (sender_id=:s AND receiver_id=:r) OR (sender_id=:r AND receiver_id=:s) ORDER BY sent_at ASC"), {"s": s, "r": r})
        # FIX: return both 'message' and 'message_text' so frontend works regardless of key used
        return jsonify([{"id": row[0], "sender_id": row[1], "receiver_id": row[2], "message_text": row[3], "message": row[3], "sent_at": str(row[4])} for row in rows])
    except: return jsonify({"message": "Server error"}), 500

@app.route("/api/messages/mark-read", methods=["POST"])
def mark_read():
    data = request.get_json()
    try:
        M = T('messages')
        db.session.execute(db.text(f"UPDATE {M} SET is_read=1 WHERE receiver_id=:r AND sender_id=:s AND is_read=0"), {"r": int(data.get("reader_id")), "s": int(data.get("sender_id"))})
        db.session.commit(); return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

# FIX: get_threads now always returns partner_id/partner_name (consistent with Messages.vue)
@app.route("/api/messages/threads")
def get_threads():
    try: uid = int(request.args.get("user_id"))
    except: return jsonify([])
    try:
        M, UN = T('messages'), T('users')
        sent = db.session.execute(db.text(f"SELECT DISTINCT receiver_id FROM {M} WHERE sender_id=:uid"), {"uid": uid}).fetchall()
        recv = db.session.execute(db.text(f"SELECT DISTINCT sender_id FROM {M} WHERE receiver_id=:uid"), {"uid": uid}).fetchall()
        partner_ids = set()
        for row in sent:
            if row[0] and int(row[0]) != uid: partner_ids.add(int(row[0]))
        for row in recv:
            if row[0] and int(row[0]) != uid: partner_ids.add(int(row[0]))
        threads = []
        for pid in partner_ids:
            partner = db.session.execute(db.text(f"SELECT id,name FROM {UN} WHERE id=:pid"), {"pid": pid}).fetchone()
            if not partner: continue
            # FIX: use subquery for Oracle compatibility instead of LIMIT1 string interpolation
            if IS_ORACLE:
                last = db.session.execute(db.text(f"SELECT message,sent_at FROM (SELECT message,sent_at,ROW_NUMBER() OVER (ORDER BY sent_at DESC) AS rn FROM {M} WHERE (sender_id=:u1 AND receiver_id=:p1) OR (sender_id=:p2 AND receiver_id=:u2)) WHERE rn=1"), {"u1": uid, "p1": pid, "p2": pid, "u2": uid}).fetchone()
            else:
                last = db.session.execute(db.text(f"SELECT message,sent_at FROM {M} WHERE (sender_id=:u1 AND receiver_id=:p1) OR (sender_id=:p2 AND receiver_id=:u2) ORDER BY sent_at DESC LIMIT 1"), {"u1": uid, "p1": pid, "p2": pid, "u2": uid}).fetchone()
            unread = db.session.execute(db.text(f"SELECT COUNT(*) FROM {M} WHERE sender_id=:p AND receiver_id=:u AND is_read=0"), {"p": pid, "u": uid}).scalar()
            threads.append({
                # FIX: always return partner_id/partner_name (Messages.vue expects these)
                "partner_id":   pid,
                "partner_name": partner[1],
                # Keep seller_id/seller_name as aliases for backwards compat
                "seller_id":    pid,
                "seller_name":  partner[1],
                "last_message": last[0] if last else "",
                "last_time":    str(last[1]) if last else "",
                "unread":       int(unread) > 0,
            })
        threads.sort(key=lambda x: x["last_time"], reverse=True)
        return jsonify(threads)
    except Exception as e:
        traceback.print_exc(); return jsonify([])

@app.route("/api/messages/unread-count")
def unread_count():
    try:
        uid = int(request.args.get("user_id"))
        return jsonify({"count": db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('messages')} WHERE receiver_id=:u AND is_read=0"), {"u": uid}).scalar()})
    except: return jsonify({"count": 0})

# ── NOTIFICATIONS ──────────────────────────────────────────────────────────
@app.route("/api/notifications")
def get_notifications():
    uid = request.args.get("user_id")
    try:
        N = T('notifications')
        if IS_ORACLE:
            rows = db.session.execute(db.text(f"SELECT id,message,is_read,created_at FROM (SELECT id,message,is_read,created_at,ROW_NUMBER() OVER (ORDER BY created_at DESC) AS rn FROM {N} WHERE user_id=:uid) WHERE rn<=30"), {"uid": int(uid)})
        else:
            rows = db.session.execute(db.text(f"SELECT id,message,is_read,created_at FROM {N} WHERE user_id=:uid ORDER BY created_at DESC LIMIT 30"), {"uid": int(uid)})
        return jsonify([{"id": r[0], "message": r[1], "is_read": r[2], "created_at": str(r[3])} for r in rows])
    except: return jsonify([])

@app.route("/api/notifications/read", methods=["POST"])
def mark_notifs_read():
    uid = request.get_json().get("user_id")
    try:
        db.session.execute(db.text(f"UPDATE {T('notifications')} SET is_read=1 WHERE user_id=:u"), {"u": uid}); db.session.commit()
        return jsonify({"message": "Marked as read"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

# ── PAYMENT ────────────────────────────────────────────────────────────────
@app.route("/api/users/<int:uid>/payment")
def get_payment(uid):
    try:
        r = db.session.execute(db.text(f"SELECT gcash_number,bank_details FROM {T('users')} WHERE id=:id"), {"id": uid}).fetchone()
        return jsonify({"gcash": r[0] if r else None, "bank": r[1] if r else None})
    except: return jsonify({"gcash": None, "bank": None})

@app.route("/api/users/<int:uid>/payment", methods=["PUT"])
def update_payment(uid):
    data = request.get_json()
    try:
        db.session.execute(db.text(f"UPDATE {T('users')} SET gcash_number=:g,bank_details=:b WHERE id=:id"), {"g": data.get("gcash"), "b": data.get("bank"), "id": uid}); db.session.commit()
        return jsonify({"message": "Payment details updated"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

# ── ADMIN ──────────────────────────────────────────────────────────────────
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    if (request.get_json() or {}).get("password") == ADMIN_PASSWORD: return jsonify({"success": True})
    return jsonify({"message": "Wrong password"}), 401

@app.route("/api/admin/stats")
def admin_stats():
    try:
        orders = blocked = 0
        try: orders = db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('orders')}")).scalar()
        except: pass
        try: blocked = db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('users')} WHERE is_blocked=1")).scalar()
        except: pass
        return jsonify({"users": db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('users')}")).scalar(), "products": db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('products')}")).scalar(), "messages": db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('messages')}")).scalar(), "orders": orders, "blocked": blocked})
    except: return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users")
def admin_users():
    try:
        UN = T('users')
        rows = db.session.execute(db.text(f"SELECT id,name,email,student_id_number,course,department,year_level,is_admin,is_blocked,block_until FROM {UN} ORDER BY id DESC"))
        result = []
        for r in rows:
            bu = None
            if r[9]:
                try: bu = r[9].strftime('%Y-%m-%dT%H:%M') if hasattr(r[9], 'strftime') else str(r[9])
                except: bu = str(r[9])
            result.append({"id": r[0], "name": r[1], "email": r[2], "student_id": r[3], "course": r[4], "department": r[5], "year_level": r[6], "is_admin": int(r[7] or 0), "is_blocked": int(r[8] or 0), "block_until": bu})
        return jsonify(result)
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users", methods=["POST"])
def admin_create_user():
    data = request.get_json() or {}; name = (data.get("name") or "").strip(); email = (data.get("email") or "").strip()
    password = data.get("password") or "adnu2024"; student_id = (data.get("student_id") or "2024-00000").strip()
    if not name or not email: return jsonify({"message": "Name and email required"}), 400
    UN = T('users')
    if db.session.execute(db.text(f"SELECT COUNT(*) FROM {UN} WHERE email=:e"), {"e": email}).scalar() > 0:
        return jsonify({"message": "Email already exists"}), 400
    try:
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        if IS_ORACLE:
            db.session.execute(db.text(f"INSERT INTO {UN} (id,name,email,password_hash,student_id_number,course,year_level,department) VALUES (users_seq.NEXTVAL,:name,:email,:pw,:sid,:course,:year,:dept)"),
                               {"name": name, "email": email, "pw": hashed, "sid": student_id, "course": data.get("course",""), "year": data.get("year_level",""), "dept": data.get("department","")})
        else:
            db.session.execute(db.text(f"INSERT INTO {UN} (name,email,password_hash,student_id_number,course,year_level,department,is_admin) VALUES (:name,:email,:pw,:sid,:course,:year,:dept,0)"),
                               {"name": name, "email": email, "pw": hashed, "sid": student_id, "course": data.get("course",""), "year": data.get("year_level",""), "dept": data.get("department","")})
        db.session.commit(); return jsonify({"message": "User created"}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/admin/users/<int:uid>", methods=["PUT"])
def admin_update_user(uid):
    data = request.get_json() or {}
    try:
        UN = T('users')
        db.session.execute(db.text(f"UPDATE {UN} SET name=:name,student_id_number=:sid,course=:course,year_level=:year,department=:dept WHERE id=:id"),
                           {"name": data.get("name"), "sid": data.get("student_id"), "course": data.get("course"), "year": data.get("year_level"), "dept": data.get("department"), "id": uid})
        if "is_admin" in data:
            db.session.execute(db.text(f"UPDATE {UN} SET is_admin=:val WHERE id=:id"), {"val": int(data["is_admin"]), "id": uid})
        db.session.commit(); return jsonify({"message": "User updated"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users/<int:uid>/block", methods=["POST"])
def admin_block_user(uid):
    data = request.get_json() or {}; action = data.get("action","block"); block_type = data.get("block_type","permanent"); duration = int(data.get("duration",1))
    try:
        UN = T('users')
        if action == "unblock":
            db.session.execute(db.text(f"UPDATE {UN} SET is_blocked=0,block_until=NULL WHERE id=:id"), {"id": uid}); db.session.commit()
            return jsonify({"message": "User unblocked"})
        block_until = None
        if block_type == "hours": block_until = datetime.now() + timedelta(hours=duration)
        elif block_type == "days": block_until = datetime.now() + timedelta(days=duration)
        if block_until:
            db.session.execute(db.text(f"UPDATE {UN} SET is_blocked=1,block_until=:bu WHERE id=:id"), {"bu": block_until, "id": uid})
        else:
            db.session.execute(db.text(f"UPDATE {UN} SET is_blocked=1,block_until=NULL WHERE id=:id"), {"id": uid})
        db.session.commit()
        return jsonify({"message": f"User blocked {'permanently' if block_type=='permanent' else f'for {duration} {block_type}'}"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
def admin_del_user(uid):
    try:
        for sql in [f"DELETE FROM {T('cart')} WHERE user_id=:id", f"DELETE FROM {T('messages')} WHERE sender_id=:id OR receiver_id=:id", f"DELETE FROM {T('notifications')} WHERE user_id=:id", f"DELETE FROM {T('orders')} WHERE buyer_id=:id OR seller_id=:id", f"DELETE FROM {T('price_history')} WHERE product_id IN (SELECT id FROM {T('products')} WHERE seller_id=:id)", f"DELETE FROM {T('products')} WHERE seller_id=:id", f"DELETE FROM {T('users')} WHERE id=:id"]:
            db.session.execute(db.text(sql), {"id": uid})
        db.session.commit(); return jsonify({"message": "User deleted"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products")
def admin_products():
    try:
        P, UN = T('products'), T('users')
        rows = db.session.execute(db.text(f"SELECT p.id,p.title,p.price,p.category,p.status,p.created_at,u.name,p.image_url,p.tags,p.description,p.seller_id FROM {P} p LEFT JOIN {UN} u ON p.seller_id=u.id ORDER BY p.id DESC"))
        result = []
        for r in rows:
            imgs = parse_images(r[7])
            result.append({"id": r[0], "title": r[1], "price": float(r[2]), "category": r[3], "status": r[4], "created_at": str(r[5]) if r[5] else None, "seller_name": r[6], "image_url": imgs[0] if imgs else None, "images": imgs, "tags": [t.strip() for t in r[8].split(",")] if r[8] else [], "description": r[9] or "", "seller_id": r[10]})
        return jsonify(result)
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/products", methods=["POST"])
def admin_create_product():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            title = (request.form.get("title") or "").strip(); price_raw = request.form.get("price","0")
            category = (request.form.get("category") or "General").strip(); seller_id = request.form.get("seller_id")
            description = (request.form.get("description") or "").strip(); tags = (request.form.get("tags") or "").strip()
            files = request.files.getlist("images") or request.files.getlist("image")
            image_url = save_images([f for f in files if f.filename]) if files else None
        else:
            data = request.get_json() or {}; title = (data.get("title") or "").strip(); price_raw = str(data.get("price") or "0")
            category = (data.get("category") or "General").strip(); seller_id = data.get("seller_id")
            description = (data.get("description") or "").strip(); tags = (data.get("tags") or "").strip(); image_url = None
        if not title or not seller_id: return jsonify({"message": "Title and seller_id required"}), 400
        try: price = float(price_raw); seller_id = int(seller_id)
        except: return jsonify({"message": "Invalid price or seller_id"}), 400
        if not db.session.execute(db.text(f"SELECT COUNT(*) FROM {T('users')} WHERE id=:id"), {"id": seller_id}).scalar():
            return jsonify({"message": "Seller not found"}), 400
        new_id = insert_product(title, description, price, category, seller_id, image_url, tags)
        db.session.commit(); track_price(new_id, price)
        return jsonify({"message": "Product created", "id": new_id}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/api/admin/products/<int:pid>", methods=["DELETE"])
def admin_del_product(pid):
    try:
        for tbl in [T('cart'), T('price_history')]:
            db.session.execute(db.text(f"DELETE FROM {tbl} WHERE product_id=:id"), {"id": pid})
        db.session.execute(db.text(f"DELETE FROM {T('products')} WHERE id=:id"), {"id": pid}); db.session.commit()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/orders")
def admin_orders():
    try:
        O, UN = T('orders'), T('users')
        if IS_ORACLE:
            rows = db.session.execute(db.text(f"SELECT id,product_title,product_price,payment_method,status,ordered_at,buyer_name,seller_name,pickup_location FROM (SELECT o.id,o.product_title,o.product_price,o.payment_method,o.status,o.ordered_at,ub.name AS buyer_name,us.name AS seller_name,o.pickup_location,ROW_NUMBER() OVER (ORDER BY o.ordered_at DESC) AS rn FROM {O} o LEFT JOIN {UN} ub ON o.buyer_id=ub.id LEFT JOIN {UN} us ON o.seller_id=us.id) WHERE rn<=100"))
        else:
            rows = db.session.execute(db.text(f"SELECT o.id,o.product_title,o.product_price,o.payment_method,o.status,o.ordered_at,ub.name,us.name,o.pickup_location FROM {O} o LEFT JOIN {UN} ub ON o.buyer_id=ub.id LEFT JOIN {UN} us ON o.seller_id=us.id ORDER BY o.ordered_at DESC LIMIT 100"))
        return jsonify([{"id": r[0], "product_title": r[1], "product_price": float(r[2]), "payment_method": r[3], "status": r[4], "ordered_at": str(r[5]) if r[5] else None, "buyer_name": r[6], "seller_name": r[7], "pickup_location": r[8]} for r in rows])
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": "Server error"}), 500

@app.route("/api/admin/messages")
def admin_messages():
    try:
        M, UN = T('messages'), T('users')
        if IS_ORACLE:
            rows = db.session.execute(db.text(f"SELECT id,sender_id,receiver_id,message,sent_at,is_read,sender_name,receiver_name FROM (SELECT m.id,m.sender_id,m.receiver_id,m.message,m.sent_at,m.is_read,u1.name AS sender_name,u2.name AS receiver_name,ROW_NUMBER() OVER (ORDER BY m.sent_at DESC) AS rn FROM {M} m LEFT JOIN {UN} u1 ON m.sender_id=u1.id LEFT JOIN {UN} u2 ON m.receiver_id=u2.id) WHERE rn<=200"))
        else:
            rows = db.session.execute(db.text(f"SELECT m.id,m.sender_id,m.receiver_id,m.message,m.sent_at,m.is_read,u1.name,u2.name FROM {M} m LEFT JOIN {UN} u1 ON m.sender_id=u1.id LEFT JOIN {UN} u2 ON m.receiver_id=u2.id ORDER BY m.sent_at DESC LIMIT 200"))
        return jsonify([{"id": r[0], "sender_id": r[1], "receiver_id": r[2], "message": r[3], "sent_at": str(r[4]) if r[4] else None, "is_read": r[5], "sender_name": r[6] or str(r[1]), "receiver_name": r[7] or str(r[2])} for r in rows])
    except: return jsonify({"message": "Server error"}), 500

# FIX: admin_analytics — removed undefined LIMIT10 variable usage, now uses the constant
@app.route("/api/admin/analytics")
def admin_analytics():
    try:
        O, P = T('orders'), T('products')
        total = db.session.execute(db.text(f"SELECT COALESCE(SUM(product_price),0) FROM {O}")).scalar()
        status_rows = db.session.execute(db.text(f"SELECT status, COUNT(*) FROM {O} GROUP BY status")).fetchall()
        by_status = {r[0]: int(r[1]) for r in status_rows if r[0]}
        # FIX: use LIMIT10 constant instead of inline string that crashed
        if IS_ORACLE:
            cat_rows = db.session.execute(db.text(f"SELECT category,COUNT(*) AS cnt FROM {P} GROUP BY category ORDER BY cnt DESC FETCH FIRST 10 ROWS ONLY")).fetchall()
        else:
            cat_rows = db.session.execute(db.text(f"SELECT category,COUNT(*) AS cnt FROM {P} GROUP BY category ORDER BY cnt DESC LIMIT 10")).fetchall()
        return jsonify({
            "total_sales":  float(total or 0),
            "by_status":    by_status,
            "tags":         [{"tag": r[0] or "General", "count": int(r[1])} for r in cat_rows if r[1] > 0],
        })
    except Exception as e:
        traceback.print_exc(); return jsonify({"message": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")