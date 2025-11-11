from flask import Flask, send_file
import os, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "../images")

app = Flask(__name__)

@app.route("/random")
def random_image():
    files = [f for f in os.listdir(IMG_DIR) if f.endswith(".jpg")]
    if not files:
        return "🚫 没有可用图片", 404
    choice = random.choice(files)
    print(f"🎲 随机展示图片：{choice}")
    return send_file(os.path.join(IMG_DIR, choice), mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(port=5000)
