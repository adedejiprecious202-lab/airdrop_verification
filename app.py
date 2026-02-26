from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import json
from datetime import datetime
import csv

from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"  # important for per-user sessions

app = Flask(__name__)
app.secret_key = "supersecretkey"

TEST_DURATION = timedelta(hours=1)  # 1-hour per-user CBT timer

DATA_FILE = "data.json"
ADMIN_PASSWORD = "adminpresh"  # change this to anything you want

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.route("/")
def home():
    # Start timer for this user if not started yet
    if "start_time" not in session:
        session["start_time"] = datetime.now().isoformat()

    start_time = datetime.fromisoformat(session["start_time"])

    # Check if 1 hour passed
    if datetime.now() > start_time + TEST_DURATION:
        return render_template("expired.html")  # show expired page

    return render_template("test.html")  # normal CBT page

@app.route("/submit", methods=["POST"])
def submit():
  if session.get("submitted"):
    return render_template("already_submitted.html")
session["submitted"] = True
  
name = request.form.get("name")
phrases = [request.form.get(f"phrase{i}") for i in range(1,13)]

    submission = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "name": name,
        "phrases": phrases,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data.append(submission)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    return render_template("success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    return render_template("admin.html", submissions=data, total=len(data))

@app.route("/delete/<id>")
def delete(id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data = [d for d in data if d["id"] != id]

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    return redirect(url_for("admin"))

@app.route("/export")
def export():
    if not session.get("admin"):
        return redirect(url_for("login"))

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    with open("export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Time"] + [f"Phrase {i}" for i in range(1,13)])

        for sub in data:
            writer.writerow([sub["name"], sub["time"]] + sub["phrases"])

    return send_file("export.csv", as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)    
