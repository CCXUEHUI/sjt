import requests, re, os
from time import sleep

BASE_URL = "https://m.tuiimg.com/meinv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "../images")
TXT_PATH = os.path.join(IMG_DIR, "files.txt")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_subpages():
    try:
        html = requests.get(BASE_URL, headers=HEADERS, timeout=10).text
        print("✅ 主页面获取成功")
        subs = re.findall(r'https://m\.tuiimg\.com/meinv/\d+', html)
        print(f"🔗 提取子页面链接数量：{len(subs)}")
        return list(set(subs))
    except Exception as e:
        print("❌ 主页面获取失败:", e)
        return []

def get_full_images(sub_url):
    try:
        html = requests.get(sub_url, headers=HEADERS, timeout=10).text
        print(f"📄 访问子页面成功：{sub_url}")
        imgs = re.findall(r'https://i\.tuiimg\.net/\S+?\.jpg', html)
        print(f"🖼️ 提取图片链接数量：{len(imgs)}")
        return list(set(imgs))
    except Exception as e:
        print(f"❌ 子页面访问失败：{sub_url}", e)
        return []

def save_image(url):
    name = url.split("/")[-1]
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        try:
            img = requests.get(url, headers=HEADERS, timeout=10).content
            with open(path, "wb") as f:
                f.write(img)
            print(f"✅ 保存图片成功：{name}")
            return True
        except Exception as e:
            print(f"❌ 保存图片失败：{url}", e)
    else:
        print(f"⚠️ 图片已存在：{name}")
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
    subpages = get_subpages()
    if not subpages:
        print("🚫 未发现任何子页面，终止爬虫")
        return
    for sub in subpages:
        img_urls = get_full_images(sub)
        if not img_urls:
            print(f"🚫 子页面无图片：{sub}")
            continue
        for img_url in img_urls:
            if save_image(img_url):
                update_txt(img_url)
            sleep(0.5)  # 避免请求过快被封

if __name__ == "__main__":
    main()
