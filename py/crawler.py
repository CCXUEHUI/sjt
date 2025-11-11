from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options)

def get_clickable_elements(driver):
    tags = ['div', 'span', 'li', 'section']
    elements = []
    for tag in tags:
        elements.extend(driver.find_elements(By.TAG_NAME, tag))
    return elements

def wait_for_url_change(driver, old_url, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.current_url != old_url)
        return True
    except:
        return False

def get_full_images(driver):
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
    driver.get(BASE_URL)
    time.sleep(3)

    elements = get_clickable_elements(driver)
    print(f"🔍 可尝试点击的元素数量：{len(elements)}")

    for i in range(len(elements)):
        try:
            elements = get_clickable_elements(driver)
            old_url = driver.current_url
            ActionChains(driver).move_to_element(elements[i]).click().perform()
            print(f"🖱️ 尝试点击第 {i+1} 个元素")

            if wait_for_url_change(driver, old_url):
                print("✅ 页面跳转成功，开始抓图")
                img_urls = get_full_images(driver)
                for url in img_urls:
                    if save_image(url):
                        update_txt(url)
                    time.sleep(0.5)
                driver.back()
                time.sleep(2)
            else:
                print("⏩ 页面未跳转，跳过该元素")
        except Exception as e:
            print(f"⚠️ 第 {i+1} 个元素处理失败：", e)
            continue

    driver.quit()

if __name__ == "__main__":
    main()
