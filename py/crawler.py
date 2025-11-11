from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import os, time, requests
from PIL import Image

BASE_URL = "https://m.tuiimg.com/meinv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "../images")
TXT_PATH = os.path.join(IMG_DIR, "files.txt")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return uc.Chrome(options=options)

def get_subpages(driver):
    driver.get(BASE_URL)
    time.sleep(2)
    try:
        main_div = driver.find_element(By.CLASS_NAME, "main")
        links = main_div.find_elements(By.TAG_NAME, "a")
        sub_urls = [link.get_attribute("href") for link in links if link.get_attribute("href") and "/meinv/" in link.get_attribute("href")]
        sub_urls = list(set(sub_urls))
        print(f"🔗 提取子页面链接数量：{len(sub_urls)}")
        return sub_urls
    except Exception as e:
        print("❌ 提取子页面失败：", e)
        return []

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
    return list(set([img.get_attribute("src") for img in imgs]))

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
        return False
    try:
        img = requests.get(url, headers=HEADERS, timeout=10).content
        with open(path, "wb") as f:
            f.write(img)
        if not is_landscape(path):
            os.remove(path)
            return False
        print(f"✅ 保存横图：{name}")
        return True
    except:
        return False

def update_txt(url):
    if not os.path.exists(TXT_PATH):
        open(TXT_PATH, "w").close()
    with open(TXT_PATH, "r+", encoding="utf-8") as f:
        lines = f.read().splitlines()
        if url not in lines:
            f.write(url + "\n")

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
