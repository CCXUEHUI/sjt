import os
import json

def main():
    # 仓库根路径
    repo_root = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(repo_root, "images")
    output_file = os.path.join(repo_root, "images.json")

    # 扫描 images 文件夹
    if not os.path.exists(images_dir):
        print("❌ images 文件夹不存在")
        return

    image_files = []
    for fname in os.listdir(images_dir):
        if fname.lower().endswith(".jpg"):
            # 拼接成 GitHub Pages 可访问的路径
            image_files.append(f"images/{fname}")

    # 写入 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(image_files, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成 {output_file}，共 {len(image_files)} 张图片")

if __name__ == "__main__":
    main()
