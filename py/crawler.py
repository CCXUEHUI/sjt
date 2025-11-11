# py/crawler.py
import requests, re, os
from html.parser import HTMLParser

BASE_URL = "https://m.tuiimg.com/meinv"
IMG_DIR = "../images"
TXT_PATH = os.path.join(IMG_DIR, "files.txt")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_subpages():
    html = requests.get(BASE_URL, headers=HEADERS).text
    return re.findall(r'https://m\.tuiimg\.com/meinv/\d+', html)

def get_full_images(sub_url):
    html = requests.get(sub_url, headers=HEADERS).text
    # 模拟“展开全图”效果：页面已加载所有图
    return re.findall(r'https://i\.tuiimg\.net/\S+?\.jpg', html)

def save_image(url):
    name = url.split("/")[-1]
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        img = requests.get(url, headers=HEADERS).content
        with open(path, "wb") as f:
            f.write(img)
        return True
    return False

def update_txt(url):
    with open(TXT_PATH, "a+", encoding="utf-8") as f:
        f.seek(0)
        lines = f.read().splitlines()
        if url not in lines:
            f.write(url + "\n")

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    for sub in get_subpages():
        for img_url in get_full_images(sub):
            if save_image(img_url):
                update_txt(img_url)

if __name__ == "__main__":
    main()
