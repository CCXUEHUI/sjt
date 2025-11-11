# py/filter.py
from PIL import Image
import os

IMG_DIR = "../images"

def is_landscape(path):
    try:
        with Image.open(path) as img:
            return img.width > img.height
    except:
        return False

def clean_portraits():
    for file in os.listdir(IMG_DIR):
        if file.endswith(".jpg"):
            path = os.path.join(IMG_DIR, file)
            if not is_landscape(path):
                os.remove(path)

if __name__ == "__main__":
    clean_portraits()
