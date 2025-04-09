"""Routers for webapp"""

# import datetime
from flask import Flask, render_template as rt, request, session, redirect
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://mongodb:27017/")
db = client["users"]

# can update this with more extensions later
valid_extensions = {"png", "jpeg", "jpg"}


def valid_file(f):
    """Checks if a valid extension is used"""
    return "." in f and f.rsplit(".", 1)[1].lower() in valid_extensions


app = Flask(__name__)


@app.route("/")
def home():
    """Routing for index"""
    return rt("home.html")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Sign up screen"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        user = {
            "username": username,
            "email": email,
            "password": password,
            "saved_transcriptions": [],
        }
        user = db.users.insert_one(user)
        session["user_id"] = str(user.inserted_id)
        return redirect("/")
    return rt("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login screen"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.users.find_one({"username": username, "password": password}) is not None:
            user = db.users.find_one({"username": username, "password": password})
            session["user_id"] = str(user["_id"])
            print(session["user_id"])
            return redirect("/home")
    return rt("login.html")


@app.route("/profile_page")
def profile():
    """Profile screen"""
    if not session.get("user_id"):
        return redirect("/home")
    user = db.users.find_one({"_id": ObjectId(session.get("user_id"))})
    return rt("profile_page.html", user=user)


@app.route("/upload", methods=["POST"])
def upload():
    """ "Reads file upload and relay to backend"""

    # Checks if an image was uploaded
    if "image" not in request.files:
        return "Error: No image uploaded"
    file = request.files["image"]
    if file.filename == "":
        return "No selected file"
    if not file or not valid_file(file.filename):
        return "Invalid file type"

    url = "http://backend:8000/upload"
    files = {"file": file}
    data = requests.post(url, files=files, timeout=3).json()
    return rt("upload.html", text=data["text"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
