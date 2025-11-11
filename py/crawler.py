from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os, time, requests
from PIL import Image

BASE_URL = "https://m.tuiimg.com/meinv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "../images")
TXT_PATH = os.path.join(IMG_DIR, "files.txt")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_subpages(driver):
    driver.get(BASE_URL)
    time.sleep(3)
    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/meinv/')]")
    sub_urls = list(set([link.get_attribute("href") for link in links if "/meinv/" in link.get_attribute("href")]))
    print(f"🔗 提取子页面链接数量：{len(sub_urls)}")
    return sub_urls

def get_full_images(driver, sub_url):
    driver.get(sub_url)
    time.sleep(2)
    try:
        btn = driver.find_element(By.XPATH, "//span[contains(text(),'展开全图')]")
        btn.click()
        time.sleep(2)
    except:
        print("⚠️ 未找到展开按钮，跳过点击")
    imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'i.tuiimg.net')]")
    img_urls = list(set([img.get_attribute("src") for img in imgs]))
    print(f"🖼️ 提取图片链接数量：{len(img_urls)}")
    return img_urls

def is_landscape(image_path):
    try:
        with Image.open(image_path) as img:
            return img.width > img.height
    except:
        return False

def save_image(url):
    name = url.split("/")[-1]
    path = os.path.join(IMG_DIR, name)
    if os.path.exists(path):
        print(f"⚠️ 图片已存在：{name}")
        return False
    try:
        img = requests.get(url, headers=HEADERS, timeout=10).content
        with open(path, "wb") as f:
            f.write(img)
        if not is_landscape(path):
            os.remove(path)
            print(f"🗑️ 删除竖图：{name}")
            return False
        print(f"✅ 保存横图成功：{name}")
        return True
    except Exception as e:
        print(f"❌ 下载失败：{url}", e)
        return False

def update_txt(url):
    if not os.path.exists(TXT_PATH):
        open(TXT_PATH, "w").close()
    with open(TXT_PATH, "r+", encoding="utf-8") as f:
        lines = f.read().splitlines()
        if url not in lines:
            f.write(url + "\n")
            print(f"📄 地址写入成功：{url}")
        else:
            print(f"⚠️ 地址已存在：{url}")

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    driver = setup_driver()
    subpages = get_subpages(driver)
    for sub in subpages:
        img_urls = get_full_images(driver, sub)
        for url in img_urls:
            if save_image(url):
                update_txt(url)
            time.sleep(0.5)
    driver.quit()

if __name__ == "__main__":
    main()
