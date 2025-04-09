"""Routers for webapp"""

# import datetime
from flask import Flask, render_template as rt, request
import requests

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
    # curr_file = {"text": data["text"], "timestamp": datetime.datetime}
    return rt("upload.html", text=data["text"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
