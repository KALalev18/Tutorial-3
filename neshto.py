# dependencies: flask, psycopg2, psycopg2.extras
# Description: This is a simple REST API that allows you to manage parts inventory.

from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# create the Flask app

app = Flask(__name__)

# configure the database connection

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "DisSys3"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# create the parts table

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL,
            specification TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            location VARCHAR(255) NOT NULL,
            supplier VARCHAR(255) NOT NULL,
            quantity INT NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()

create_table()

# define the routes

# select all parts

@app.route("/parts", methods=["GET"])
def get_parts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts")
    parts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(parts)

# insert a new part

@app.route("/parts", methods=["POST"])
def add_part():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO parts (name, type, specification, price, location, supplier, quantity) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (data["name"], data["type"], data["specification"], data["price"], data["location"], data["supplier"], data["quantity"]),
        )
        part_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": part_id, "message": "Part added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# delete a part

@app.route("/parts/<int:part_id>", methods=["GET"])
def get_part(part_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts WHERE id = %s", (part_id,))
    part = cur.fetchone()  # Fetch a single record
    cur.close()
    conn.close()
    if part:
        return jsonify(part)
    else:
        return jsonify({"error": "Part not found"}), 404

# update a part

@app.route("/parts/<int:part_id>", methods=["PUT"])
def update_part(part_id):
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE parts SET name = %s, type = %s, specification = %s, price = %s, location = %s, supplier = %s, quantity = %s WHERE id = %s",
            (data["name"], data["type"], data["specification"], data["price"], data["location"], data["supplier"], data["quantity"], part_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Part updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# specific queries

@app.route("/parts/type/<string:part_type>", methods=["GET"])
def get_parts_by_type(part_type):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts WHERE type = %s", (part_type,))
    parts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(parts)

@app.route("/parts/location/<string:location>", methods=["GET"])
def get_parts_by_location(location):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts WHERE location = %s", (location,))
    parts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(parts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)