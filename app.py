from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this to something strong

# -------------------- SETTINGS --------------------
# Admin password
ADMIN_PASSWORD = "mypassword"  # change to your desired password

# Storage for submissions (in-memory for testing)
submissions = []

# Each session lasts 1 hour from first visit
app.permanent_session_lifetime = timedelta(hours=1)

# -------------------- SESSION TIMER --------------------
@app.before_request
def make_session_permanent():
    session.permanent = True
    if "expiry" in session:
        if datetime.now() > session["expiry"]:
            session.clear()  # session expired, clear everything

# -------------------- ROUTES --------------------
@app.route("/")
def test():
    # Set expiry if not already set
    if "expiry" not in session:
        session["expiry"] = datetime.now() + timedelta(hours=1)
    return render_template("test.html")

@app.route("/submit", methods=["POST"])
def submit():
    # Block submission if expired
    if "expiry" in session and datetime.now() > session["expiry"]:
        return render_template("expired.html")

    #
