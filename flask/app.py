from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import math

app = Flask(__name__)

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("routes.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Pages ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/history")
def history():
    conn = sqlite3.connect("routes.db")
    rows = conn.execute(
        "SELECT latitude, longitude, time FROM routes ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("history.html", rows=rows)

# ---------- Location Update & Anomaly Detection ----------
@app.route("/update_location", methods=["POST"])
def update_location():
    lat = float(request.form["lat"])
    lon = float(request.form["lon"])

    conn = sqlite3.connect("routes.db")

    # Get previous locations
    rows = conn.execute(
        "SELECT latitude, longitude FROM routes"
    ).fetchall()

    status = "SAFE"

    # Learn routine after first 3 records
    if len(rows) >= 3:
        avg_lat = sum(r[0] for r in rows) / len(rows)
        avg_lon = sum(r[1] for r in rows) / len(rows)

        # Distance from routine
        distance = math.sqrt((lat - avg_lat)**2 + (lon - avg_lon)**2)

        # Threshold (increase if needed)
        if distance > 0.05:
            status = "SOS"

    # Save current location
    conn.execute(
        "INSERT INTO routes (latitude, longitude, time) VALUES (?, ?, ?)",
        (lat, lon, datetime.now())
    )
    conn.commit()
    conn.close()

    return jsonify({"status": status})

if __name__ == "__main__":
    app.run(debug=True)
