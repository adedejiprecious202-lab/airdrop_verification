from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Change this to something strong

# ---------------- SETTINGS ----------------
ADMIN_PASSWORD = "adminpresh"  # Change this
submissions = []  # stores all submissions
app.permanent_session_lifetime = timedelta(hours=1)  # each session lasts 1 hour

# ---------------- SESSION TIMER ----------------
@app.before_request
def make_session_permanent():
    session.permanent = True
    if "expiry" in session:
        if datetime.now() > session["expiry"]:
            session.clear()  # clear session if expired

# ---------------- ROUTES ----------------
@app.route("/")
def test():
    if "expiry" not in session:
        session["expiry"] = datetime.now() + timedelta(hours=1)
    return render_template("test.html")

@app.route("/submit", methods=["POST"])
def submit():
    if "expiry" in session and datetime.now() > session["expiry"]:
        return render_template("expired.html")
    if "submitted" in session:
        return render_template("expired.html")

    name = request.form.get("name")
    codes = [request.form.get(f"code{i}") for i in range(1,13)]

    submissions.append({
        "name": name,
        "codes": codes,
        "time_submitted": datetime.now().strftime("%H:%M:%S")
    })

    session["submitted"] = True

    return render_template("success.html")

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            return "Incorrect password", 401
    return render_template("login.html")

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("admin.html", submissions=submissions)

@app.route("/delete/<int:index>")
def delete_submission(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    try:
        submissions.pop(index)
    except IndexError:
        pass
    return redirect(url_for("admin_panel"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
