"""Routers for machine learning client"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename as sf
from PIL import Image
import pytesseract
from pytesseract import Output
import cv2
from pymongo import MongoClient

# mongodb compass connection string is mongodb://localhost:27017
client = MongoClient("mongodb://mongodb:27017/")

db = client["epic-metal-machine"]
collection = db["entries"]


app = Flask(__name__)
UPLOADS = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOADS

# can update this with more extensions later
valid_extensions = {"png", "jpeg", "jpg"}


def valid_file(f):
    """Checks if a valid extension is used"""
    return "." in f and f.rsplit(".", 1)[1].lower() in valid_extensions


@app.route("/upload", methods=["POST"])
def upload():
    """Routing for upload"""

    file = request.files["file"]
    user_id = request.form.get("id")
    filename = sf(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    cv_img = cv2.imread(filepath)
    # os.remove(filepath)
    # Removes color from the image. I think this should improve performance in theory but
    # maybe there's a situation where this will actually cause problems? idk. also ups the
    # contrast of the image
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    processed_pil = Image.fromarray(thresh)
    # run tesseract
    data = pytesseract.image_to_data(
        processed_pil, config="--oem 3 --psm 6", output_type=Output.DICT
    )
    lines = {}
    # loop through words again and remove ones from transcription with low confidence
    for i in range(len(data["text"])):
        word = data["text"][i]
        conf = int(data["conf"][i])
        line_num = data["line_num"][i]
        # feel free to toy around with this number-- it represents a confidence threshold and
        # any text that falls below it will not be included in the transcription. Not sure if 40
        # is a good value or not
        if conf > 40 and word.strip():
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(word.strip())
    extracted = "\n".join([" ".join(line_words) for line_words in lines.values()])
    data = {
        "date-time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": user_id,
        "text": extracted,
    }
    collection.insert_one(data)

    return jsonify({"status": "successful"}), 200


if __name__ == "__main__":
    os.makedirs(UPLOADS, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=True)
