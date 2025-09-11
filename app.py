# app.py
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
from models.face_recognition import recognize_face
import os

app = Flask(__name__)

# --- Home page ---
@app.route("/")
def index():
    return render_template("index.html")

# --- Upload endpoint for sending webcam frames ---
@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json["image"]
        img_data = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        
        result = recognize_face(frame)

        return jsonify({"result": result})
    except Exception as e:
        print("Error in /upload:", e)
        return jsonify({"result": "Error processing image"}), 500


if __name__ == "__main__":
    app.run(debug=True)
