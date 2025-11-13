import os
import time
import shutil
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

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
    print(f"🌐 正在访问主页面：{BASE_URL}")
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

def get_chrome_path():
    candidates = [
        shutil.which("google-chrome-stable"),
        shutil.which("google-chrome"),
        shutil.which("chromium-browser"),
        "/opt/google/chrome/google-chrome"
    ]
    for path in candidates:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            print(f"✅ 使用 Chrome 路径: {path}")
            return path
    raise RuntimeError("未找到可用的 Chrome 可执行文件")

def get_chromedriver_path():
    driver_path = shutil.which("chromedriver")
    if driver_path and os.path.exists(driver_path) and os.access(driver_path, os.X_OK):
        print(f"✅ 使用 chromedriver 路径: {driver_path}")
        return driver_path
    raise RuntimeError("未找到可用的 chromedriver")

def extract_image_urls(page_url):
    print(f"📄 打开子页面：{page_url}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    chrome_path = get_chrome_path()
    options.binary_location = chrome_path

    driver_path = get_chromedriver_path()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    driver.get(page_url)
    time.sleep(3)

    # 模拟点击“展开全图”
    try:
        expand_btn = driver.find_element(By.XPATH, "//a[contains(text(),'展开全图')]")
        expand_btn.click()
        time.sleep(3)
    except Exception:
        print("⚠️ 未找到展开按钮，可能页面已直接显示全部图片")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    img_urls = set()
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("https://i.tuiimg.net") and src.endswith(".jpg"):
            img_urls.add(src)

    print(f"🖼️ 提取到 {len(img_urls)} 张图片")
    return list(img_urls)

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
            save_image(url)
    clean_files_txt()

if __name__ == "__main__":
    main()
