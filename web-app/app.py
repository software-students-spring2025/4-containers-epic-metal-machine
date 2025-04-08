"""Routers for webapp"""

import os
from flask import Flask, render_template as rt, request
from werkzeug.utils import secure_filename as sf

UPLOADS = "static/uploads"
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOADS


@app.route("/")
def home():
    """Routing for index"""
    return rt("home.html")

@app.route("/recieve_data", methods=["POST"])
def recieve_data():
    data = request.get_json()
    return rt("upload.html")


if __name__ == "__main__":
    os.makedirs(UPLOADS, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=True)
