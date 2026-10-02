from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# ==============================
# DATABASE INITIALIZATION
# ==============================

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Default admin user
    cursor.execute("""
        INSERT OR IGNORE INTO users (email, password)
        VALUES (?, ?)
    """, ("admin@gmail.com", "1234"))

    # Waste Collection table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            quantity TEXT NOT NULL,
            address TEXT NOT NULL,
            message TEXT
        )
    """)

    # If old table already exists without message column
    try:
        cursor.execute("ALTER TABLE waste_collection ADD COLUMN message TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# ==============================
# HOME
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return dashboard()

        return "Invalid email or password"

    return render_template("login.html")


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, waste_type, quantity, address, message
        FROM waste_collection
        ORDER BY id DESC
    """)

    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        requests=requests
    )


# ==============================
# WASTE COLLECTION
# ==============================

@app.route("/waste-collection", methods=["GET", "POST"])
def waste_collection():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        address = request.form["address"]
        waste_type = request.form["waste_type"]
        quantity = request.form["quantity"]
        message = request.form.get("message", "")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO waste_collection
            (name, email, waste_type, quantity, address, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            waste_type,
            quantity,
            address,
            message
        ))

        conn.commit()
        conn.close()

        return """
        <h2>Waste collection request submitted successfully!</h2>
        <br>
        <a href="/waste-collection">Submit another request</a>
        <br><br>
        <a href="/dashboard">View Dashboard</a>
        """

    return render_template("waste-collection.html")


# ==============================
# TRACKING
# ==============================

@app.route("/tracking")
def tracking():
    return render_template("tracking.html")


# ==============================
# COMPLAINTS
# ==============================

@app.route("/complaints")
def complaints():
    return render_template("complaints.html")


# ==============================
# REPORTS
# ==============================

@app.route("/reports")
def reports():
    return render_template("reports.html")


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)