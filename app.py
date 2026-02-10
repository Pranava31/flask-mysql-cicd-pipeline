import os
from flask import Flask, render_template, request, redirect, url_for

import MySQLdb

app = Flask(__name__)

db_host = os.environ.get("MYSQL_HOST", "localhost")
db_user = os.environ.get("MYSQL_USER", "root")
db_password = os.environ.get("MYSQL_PASSWORD", "root")
db_name = os.environ.get("MYSQL_DB", "devops_notes")


def get_db_connection():
    connection = MySQLdb.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        db=db_name
    )
    return connection


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100) DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category = request.form.get("category", "General")
        cursor.execute(
            "INSERT INTO notes (title, content, category) VALUES (%s, %s, %s)",
            (title, content, category)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("index"))

    cursor.execute("SELECT id, title, content, category, created_at FROM notes ORDER BY created_at DESC")
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", notes=notes)


@app.route("/delete/<int:note_id>")
def delete(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
