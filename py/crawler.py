import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = "https://m.tuiimg.com/meinv"
IMG_DIR = "images"
TXT_PATH = os.path.join(IMG_DIR, "files.txt")

os.makedirs(IMG_DIR, exist_ok=True)
existing_urls = set()

# 读取已保存的地址，避免重复
if os.path.exists(TXT_PATH):
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        existing_urls = set(line.strip() for line in f if line.strip())

def is_landscape(img: Image.Image) -> bool:
    return img.width > img.height

def save_image(url: str):
    if url in existing_urls:
        return
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(BytesIO(resp.content))
        if is_landscape(img):
            filename = os.path.basename(url)
            path = os.path.join(IMG_DIR, filename)
            img.save(path)
            with open(TXT_PATH, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            print(f"✅ Saved: {url}")
        else:
            print(f"⛔ Skipped (portrait): {url}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

def get_subpages():
    resp = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a", href=True)
    return [f"https://m.tuiimg.com{a['href']}" for a in links if a["href"].startswith("/meinv/")]

def extract_image_urls(page_url):
    resp = requests.get(page_url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    # 模拟“展开全图”后的图片地址
    return [img["src"] for img in soup.find_all("img", src=True) if img["src"].startswith("https://i.tuiimg.net") and img["src"].endswith(".jpg")]

def main():
    subpages = get_subpages()
    for page in subpages:
        print(f"🔍 Visiting: {page}")
        img_urls = extract_image_urls(page)
        for url in img_urls:
            save_image(url)

if __name__ == "__main__":
    main()
