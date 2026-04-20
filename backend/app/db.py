import oracledb

# --- ORACLE INITIALIZATION ---
try:
    # Update this path to your local Instant Client folder
    oracledb.init_oracle_client(lib_dir=r"C:\Users\Lito\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_2")
except Exception as e:
    print(f"Oracle Client already initialized or Error: {e}")

DB_CONFIG = {
    "user": "system",
    "password": "root",
    "dsn": "localhost:1521/XE"
}

def get_connection():
    return oracledb.connect(**DB_CONFIG)

# --- USER FUNCTIONS ---
def register_user(name, email, password_hash, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # ID is handled by users_trigger in Oracle
        sql = "INSERT INTO users (name, email, password_hash, role) VALUES (:1, :2, :3, :4)"
        cursor.execute(sql, [name, email, password_hash, role])
        conn.commit()
        return True
    except Exception as e:
        print(f"Register Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email = :1", [email])
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2], "password_hash": row[3], "role": row[4]}
        return None
    finally:
        cursor.close()
        conn.close()

# --- PRODUCT FUNCTIONS ---
def add_product(title, description, price, category, seller_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # ID is handled by products_trigger in Oracle
        sql = "INSERT INTO products (title, description, price, category, seller_id) VALUES (:1, :2, :3, :4, :5)"
        cursor.execute(sql, [title, description, price, category, seller_id])
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Product Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Per MVP: Only show Available items
        cursor.execute("SELECT id, title, description, price, category, status FROM products WHERE status = 'Available'")
        columns = [col.lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def get_my_products(seller_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, price, status FROM products WHERE seller_id = :1", [seller_id])
        columns = [col.lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()
