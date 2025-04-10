"""Routers for webapp"""

# import datetime
from flask import (
    Flask,
    render_template as rt,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient("mongodb://mongodb:27017/")
db = client["epic-metal-machine"]
collection = db["entries"]

# can update this with more extensions later
valid_extensions = {"png", "jpeg", "jpg"}


def valid_file(f):
    """Checks if a valid extension is used"""
    return "." in f and f.rsplit(".", 1)[1].lower() in valid_extensions


app = Flask(__name__)
app.secret_key = "your_secret_key_here"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    """User class"""

    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        """checks password"""
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    """Load user callback"""
    user_data = db["users"].find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data["_id"], user_data["username"], user_data["password"])
    return None


@app.route("/")
@login_required
def home():
    """Routing for index"""
    return rt("home.html")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Sign up screen"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = {
            "username": username,
            "password": generate_password_hash(password),
        }
        user = db["users"].insert_one(user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return rt("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login screen"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Look for the user in our in-memory database
        user_data = db["users"].find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            login_user(
                User(user_data["_id"], user_data["username"], user_data["password"])
            )
            flash("Logged in successfully.")
            return redirect(url_for("home"))

        flash("Invalid username or password")
        return redirect(url_for("login"))
    return rt("login.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    """Reads file upload and relay to backend"""

    # Checks if an image was uploaded
    if "image" not in request.files:
        return "Error: No image uploaded"
    file = request.files["image"]
    if file.filename == "":
        return "No selected file"
    if not file or not valid_file(file.filename):
        return "Invalid file type"

    url = "http://backend:8000/upload"
    file = {"file": file}
    data = {"id": current_user.id}
    requests.post(url, files=file, data=data, timeout=3)
    return redirect(url_for("history"))


@app.route("/history", methods=["GET"])
@login_required
def history():
    """Return OCR history"""

    entries = collection.find({"user_id": str(current_user.id)})
    print(current_user.id)
    return rt("history.html", entries=entries)


@app.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
