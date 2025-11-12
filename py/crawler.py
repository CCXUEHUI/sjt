import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = "https://m.tuiimg.com/meinv/"
IMG_DIR = "images"
TXT_PATH = os.path.join(IMG_DIR, "files.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 EdgA/136.0.0.0"
}

# 创建 images 文件夹
os.makedirs(IMG_DIR, exist_ok=True)

# 已保存的地址集合
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
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 在 li 标签下查找所有 a 标签
        links = soup.find_all("li")
        subpages = set()
        for li in links:
            a_tags = li.find_all("a", href=True)
            for a in a_tags:
                href = a["href"]
                if href.startswith("https://m.tuiimg.com/meinv/"):
                    subpages.add(href)

        print(f"📊 总共获取到 {len(subpages)} 个有效子页面链接")
        return list(subpages)
    except Exception as e:
        print(f"❌ 获取子页面失败：{e}")
        return []

def extract_image_urls(page_url):
    try:
        print(f"📄 访问子页面：{page_url}")
        resp = requests.get(page_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 模拟点击“展开全图”，直接查找完整页面中的图片
        img_tags = soup.find_all("img", src=True)
        img_urls = set()
        for img in img_tags:
            src = img["src"]
            if src.startswith("https://i.tuiimg.net") and src.endswith(".jpg"):
                img_urls.add(src)

        print(f"🖼️ 提取到 {len(img_urls)} 张图片")
        return list(img_urls)
    except Exception as e:
        print(f"❌ 提取图片失败：{page_url}，错误：{e}")
        return []

def main():
    subpages = get_subpages()
    if not subpages:
        print("⚠️ 没有子页面，终止任务")
        return
    for page in subpages:
        img_urls = extract_image_urls(page)
        for url in img_urls:
            save_image(url)

if __name__ == "__main__":
    main()
