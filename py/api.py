from flask import Flask, send_file
import os, random

app = Flask(__name__)
IMG_DIR = "images"

@app.route("/random")
def random_image():
    files = [f for f in os.listdir(IMG_DIR) if f.endswith(".jpg")]
    if not files:
        return "No images available", 404
    choice = random.choice(files)
    return send_file(os.path.join(IMG_DIR, choice), mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(port=5000)
