import oracledb
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# --- ORACLE INIT ---
try:
    oracledb.init_oracle_client(
        lib_dir=r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_26"
    )
except Exception as e:
    print(f"Oracle Error: {e}")

app = Flask(__name__)

# --- CONFIG ---
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "oracle+oracledb://dotado:202400926@localhost:1521/?service_name=XE"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return "Backend is running!"

# ---------------- AUTH ---------------- #

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email", "")
    student_id = data.get("student_id_number", "")

    # ✅ EMAIL VALIDATION
    if not email.endswith("@gbox.adnu.edu.ph"):
        return jsonify({"message": "Use ADNU GBOX email only"}), 400

    # ✅ STUDENT ID VALIDATION
    if "-" not in student_id:
        return jsonify({"message": "Student ID must contain '-'"}), 400

    # ✅ CHECK DUPLICATE
    existing = db.session.execute(
        db.text("SELECT COUNT(*) FROM USERS WHERE email = :email"),
        {"email": email}
    ).scalar()

    if existing > 0:
        return jsonify({"message": "Email already registered"}), 400

    hashed_pw = bcrypt.generate_password_hash(data.get("password")).decode("utf-8")

    try:
        db.session.execute(db.text("""
            INSERT INTO USERS (
                id, name, email, password_hash,
                student_id_number, course, year_level, department
            )
            VALUES (
                users_seq.NEXTVAL,
                :name,
                :email,
                :pw,
                :student_id,
                :course,
                :year,
                :dept
            )
        """), {
            "name": data.get("name"),
            "email": email,
            "pw": hashed_pw,
            "student_id": student_id,
            "course": data.get("course"),
            "year": data.get("year_level"),
            "dept": data.get("department")
        })

        db.session.commit()
        return jsonify({"message": "Registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    res = db.session.execute(
        db.text("""
            SELECT id, name, email, password_hash,
                   student_id_number, course, year_level, department
            FROM USERS
            WHERE email = :email
        """),
        {"email": data.get("email")}
    ).fetchone()

    if not res:
        return jsonify({"message": "User not found"}), 404

    stored_password = str(res[3])

    if bcrypt.check_password_hash(stored_password, data.get("password")):
        return jsonify({
            "user_id": res[0],
            "name": res[1],
            "email": res[2],
            "student_id_number": res[4],
            "course": res[5],
            "year_level": res[6],
            "department": res[7]
        })

    return jsonify({"message": "Invalid password"}), 401


# ---------------- PRODUCTS ---------------- #

@app.route("/api/products", methods=["GET"])
def get_products():
    result = db.session.execute(db.text("""
        SELECT id, title, description, price, category, status
        FROM PRODUCTS
        WHERE status = 'Available'
        ORDER BY id DESC
    """))

    products = []

    for row in result:
        products.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": float(row[3]),
            "category": row[4],
            "status": row[5]
        })

    return jsonify(products)


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    try:
        db.session.execute(db.text("""
            INSERT INTO PRODUCTS (
                id, title, description, price,
                category, pickup_location, seller_id, created_at, status
            )
            VALUES (
                products_seq.NEXTVAL,
                :title,
                :description,
                :price,
                :category,
                :pickup_location,
                :seller_id,
                SYSDATE,
                'Available'
            )
        """), {
            "title": data.get("title"),
            "description": data.get("description"),
            "price": data.get("price"),
            "category": data.get("category", "General"),
            "pickup_location": data.get("pickup_location", "N/A"),
            "seller_id": data.get("user_id")
        })

        db.session.commit()
        return jsonify({"message": "Product created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True, port=5000)