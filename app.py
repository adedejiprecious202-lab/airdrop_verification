from flask import Flask, render_template, request, redirect, session, url_for
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change to a strong secret in production
app.permanent_session_lifetime = timedelta(hours=1)  # session expires in 1 hour

# Storage for submissions (in-memory for testing; use DB for production)
submissions = []

# Admin password
ADMIN_PASSWORD = "mypassword"  # change to whatever you want

# -------------------- ROUTES --------------------

@app.route("/")
def test():
    return render_template("test.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    codes = [request.form.get(f"code{i}") for i in range(1, 13)]

    # Prevent multiple submissions per session
    if "submitted" in session:
        return render_template("expired.html")
    session["submitted"] = True

    # Store submission
    submissions.append({
        "name": name,
        "codes": codes
    })
    return render_template("success.html")

@app.route("/admin-login", methods=["GET", "POST"])
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

# -------------------- RUN --------------------

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
