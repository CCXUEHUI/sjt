from flask import Flask, Response
import os
import random

app = Flask(__name__)

# 仓库根路径下的 files.txt
TXT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../files.txt")

def load_urls():
    if not os.path.exists(TXT_PATH):
        return []
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

@app.route("/random")
def random_url():
    urls = load_urls()
    if not urls:
        return Response("🚫 没有可用图片地址", status=404)
    choice = random.choice(urls)
    print(f"🎲 随机选择图片地址：{choice}")
    return Response(choice, mimetype="text/plain")

if __name__ == "__main__":
    app.run(port=5000)
