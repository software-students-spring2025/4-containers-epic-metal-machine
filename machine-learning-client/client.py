"""Routers for webapp"""

import os
from flask import render_template as rt, Flask, request
from werkzeug.utils import secure_filename as sf
from PIL import Image
import pytesseract
from pytesseract import Output
import cv2
import numpy as np

app = Flask(__name__)

# can update this with more extensions later
valid_extensions = {"png", "jpeg", "jpg"} 

def valid_file(f):
    """Checks if a valid extension is used"""
    return "." in f and f.rsplit(".", 1)[1].lower() in valid_extensions

@app.route("/upload", methods=["POST"])
def upload():
    """Routing for upload"""

    print("======== YESSIRSEawidbawdawdwadad ========")

    # Checks if an image was uploaded
    if "image" not in request.files:
        return "Error: No image uploaded"
    file = request.files["image"]
    if file.filename == "":
        return "No selected file"
    if not file or not valid_file(file.filename):
        return "Invalid file type"

    filename = sf(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    cv_img = cv2.imread(filepath)
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
    box_path = draw_boxes(filename, processed_pil, data)
    lines = {}
    # loop through words again and remove ones from transcription with low confidence
    # will figure out how to just make this one loop instead of two at a later date
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
    return rt("upload.html", image_file=filepath, boxed_image=box_path, text=extracted)


def draw_boxes(filename, processed_pil, data):
    "Draw boxes, save image, and return path to image"

    boxes = cv2.cvtColor(np.array(processed_pil), cv2.COLOR_RGB2BGR)
    # loops through each word and adds box around it on image
    for i in range(len(data["text"])):
        word = data["text"][i]
        conf = int(data["conf"][i])
        # feel free to toy around with this number-- it represents a confidence threshold for
        # drawing boundary boxes on the image. Anything that falls below it will not be included
        # in the transcription. Not sure if 60 is a good value or not '''
        if conf > 60 and word.strip():
            x, y, w, h = (
                data["left"][i],
                data["top"][i],
                data["width"][i],
                data["height"][i],
            )
            # could  change the look of the box on the image by tweaking this @ Johnny and Sophia
            # x --> left-most x pixel
            # y  --> top-most y pixel
            # w --> width
            # h --> height '''
            cv2.rectangle(boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # save new image with added boxes
    box_filename = "box_" + filename
    box_path = os.path.join("static/processed", box_filename)
    cv2.imwrite(box_path, boxes)
    return box_path