import os

from flask import Flask, request, jsonify
import psycopg2


app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "my-site-db"),
        database=os.getenv("POSTGRES_DB", "mydatabase"),
        user=os.getenv("POSTGRES_USER", "myuser"),
        password=os.getenv("POSTGRES_PASSWORD", "mypassword"),
    )


def init_db():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


@app.route("/api/users", methods=["GET"])
def get_users():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM users ORDER BY id")

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify([
        {
            "id": user[0],
            "name": user[1]
        }
        for user in users
    ])


@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO users (name) VALUES (%s)",
        (name,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )
