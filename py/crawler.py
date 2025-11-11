import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = "https://m.tuiimg.com/meinv"
IMG_DIR = "images"
TXT_PATH = os.path.join(IMG_DIR, "files.txt")

# 模拟 Android + Via 浏览器 UA
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.93 Mobile Safari/537.36 Via/4.3.9"
}

# 创建 images 文件夹
os.makedirs(IMG_DIR, exist_ok=True)

# 读取已保存的地址，避免重复下载
existing_urls = set()
if os.path.exists(TXT_PATH):
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        existing_urls = set(line.strip() for line in f if line.strip())

def is_landscape(img: Image.Image) -> bool:
    return img.width > img.height

def save_image(url: str):
    if url in existing_urls:
        print(f"🔁 已存在，跳过：{url}")
        return
    try:
        print(f"⬇️ 正在下载图片：{url}")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        print(f"📐 图片尺寸：{img.width}x{img.height}")
        if is_landscape(img):
            filename = os.path.basename(url)
            path = os.path.join(IMG_DIR, filename)
            img.save(path)
            with open(TXT_PATH, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            print(f"✅ 已保存横图：{filename}")
        else:
            print(f"⛔ 跳过竖图：{url}")
    except Exception as e:
        print(f"❌ 下载失败：{url}，错误：{e}")

def get_subpages():
    try:
        print(f"🌐 正在访问主页面：{BASE_URL}")
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        print(f"📄 页面状态码：{resp.status_code}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        main_div = soup.find("div", class_="main")
        if not main_div:
            print("⚠️ 页面中未找到 class='main' 的 div")
            return []
        links = main_div.find_all("a", href=True)
        subpages = [f"https://m.tuiimg.com{a['href']}" for a in links if a["href"].startswith("/meinv/")]
        print(f"🔗 获取到 {
