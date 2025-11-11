import requests, re, os

BASE_URL = "https://m.tuiimg.com/meinv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "../images")
TXT_PATH = os.path.join(IMG_DIR, "files.txt")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_subpages():
    html = requests.get(BASE_URL, headers=HEADERS).text
    return list(set(re.findall(r'https://m\.tuiimg\.com/meinv/\d+', html)))

def get_full_images(sub_url):
    html = requests.get(sub_url, headers=HEADERS).text
    return list(set(re.findall(r'https://i\.tuiimg\.net/\S+?\.jpg', html)))

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
    if not os.path.exists(TXT_PATH):
        open(TXT_PATH, "w").close()
    with open(TXT_PATH, "r+", encoding="utf-8") as f:
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
