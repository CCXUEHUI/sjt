import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = "https://m.tuiimg.com/meinv/list_5.html"
TXT_PATH = os.path.join(repo_root, "images", "files.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 EdgA/136.0.0.0"
}

# 已保存的地址集合
existing_urls = set()
if os.path.exists(TXT_PATH):
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        existing_urls = set(line.strip() for line in f if line.strip())

def is_landscape(img: Image.Image) -> bool:
    return img.width > img.height

def url_is_valid(url: str) -> bool:
    return bool(re.search(r"/\d+\.jpg$", url))

def save_url_if_landscape(url: str):
    if url in existing_urls:
        print(f"🔁 已存在，跳过：{url}")
        return True
    if not url_is_valid(url):
        print(f"⚠️ 非数字.jpg结尾，跳过：{url}")
        return False
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"❌ 无法访问：{url}")
            return False
        img = Image.open(BytesIO(resp.content))
        if is_landscape(img):
            with open(TXT_PATH, "a", encoding="utf-8") as f:
                f.write(url + "\n")
            print(f"✅ 已记录横屏地址：{url}")
            return True
        else:
            print(f"⛔ 跳过竖屏：{url}")
            return True
    except Exception as e:
        print(f"❌ 请求失败：{url}，错误：{e}")
        return False

def get_subpages():
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    subpages = set()
    for li in soup.find_all("li"):
        for a in li.find_all("a", href=True):
            href = a["href"]
            if href.startswith("https://m.tuiimg.com/meinv/"):
                subpages.add(href)
    print(f"📊 总共获取到 {len(subpages)} 个有效子页面链接")
    return list(subpages)

def extract_image_urls(page_url):
    resp = requests.get(page_url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    img_urls = set()
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("https://i.tuiimg.net") and src.endswith(".jpg"):
            img_urls.add(src)
    print(f"🖼️ 提取到 {len(img_urls)} 张图片")
    return list(img_urls)

def crawl_sequence(start_url: str):
    match = re.search(r"(.*?/)(\d+)\.jpg$", start_url)
    if not match:
        return
    base, num = match.groups()
    num = int(num)
    start_num = num
    end_num = num
    while True:
        url = f"{base}{num}.jpg"
        success = save_url_if_landscape(url)
        if not success:
            break
        end_num = num
        num += 1
    print(f"📌 序列范围: {base}{start_num}.jpg → {base}{end_num}.jpg")

def clean_files_txt():
    if os.path.exists(TXT_PATH):
        with open(TXT_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        with open(TXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(set(lines))) + "\n")
        print(f"🧹 已清理 files.txt，当前记录 {len(lines)} 条")

def main():
    subpages = get_subpages()
    if not subpages:
        print("⚠️ 没有子页面，终止任务")
        return
    for page in subpages:
        img_urls = extract_image_urls(page)
        for url in img_urls:
            if url_is_valid(url):
                crawl_sequence(url)
    clean_files_txt()

if __name__ == "__main__":
    main()
