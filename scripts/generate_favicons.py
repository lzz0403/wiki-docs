import os
import sys
import base64
from io import BytesIO
from PIL import Image

def crop_center_square(img):
    width, height = img.size
    new_edge = min(width, height)
    
    left = (width - new_edge) / 2
    top = (height - new_edge) / 2
    right = (width + new_edge) / 2
    bottom = (height + new_edge) / 2
    
    return img.crop((left, top, right, bottom))

def generate_icons(source_path, output_dir="public"):
    if not os.path.exists(source_path):
        print(f"错误：找不到源文件 {source_path}")
        return

    if not os.path.exists(output_dir):
        print(f"创建输出目录：{output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    try:
        img = Image.open(source_path)
    except Exception as e:
        print(f"无法打开图片：{e}")
        return

    # 确保图片是正方形，如果不是则裁剪
    if img.size[0] != img.size[1]:
        print("图片不是正方形，正在进行中心裁剪...")
        img = crop_center_square(img)

    # 定义目标文件及其尺寸
    targets = [
        ("android-chrome-192x192.png", (192, 192)),
        ("android-chrome-512x512.png", (512, 512)),
        ("apple-touch-icon.png", (180, 180)),
        ("favicon-16x16.png", (16, 16)),
        ("favicon-32x32.png", (32, 32)),
        ("mstile-150x150.png", (270, 270)), # 实际上是 270x270
    ]

    print("开始生成图片...")

    # 生成 PNG 文件
    for filename, size in targets:
        out_path = os.path.join(output_dir, filename)
        resized_img = img.resize(size, Image.Resampling.LANCZOS)
        resized_img.save(out_path)
        print(f"已生成：{out_path} ({size[0]}x{size[1]})")

    # 生成 favicon.ico
    ico_path = os.path.join(output_dir, "favicon.ico")
    # 增加更多大尺寸以适应高分屏和桌面快捷方式 (最高支持 256x256)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for size in ico_sizes:
        ico_images.append(img.resize(size, Image.Resampling.LANCZOS))
    
    # save() 方法可以将多个图像保存为一个 ICO 文件
    ico_images[0].save(ico_path, format='ICO', sizes=[(i.width, i.height) for i in ico_images], append_images=ico_images[1:])
    print(f"已生成：{ico_path} (含尺寸: {ico_sizes})")

    # 生成 safari-pinned-tab.svg (嵌入式 PNG)
    # 注意: 标准的 Safari Pinned Tab 图标应该是单色矢量路径 (Path)。
    # 这里的实现是将 PNG 转为 Base64 嵌入到 SVG 中，这是一个兼容性方案。
    safari_path = os.path.join(output_dir, "safari-pinned-tab.svg")
    safari_size = (512, 512)
    safari_img = img.resize(safari_size, Image.Resampling.LANCZOS)
    
    buffered = BytesIO()
    safari_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    svg_content = f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {safari_size[0]} {safari_size[1]}">
 <image width="100%" height="100%" href="data:image/png;base64,{img_str}" />
</svg>"""
    
    with open(safari_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"已生成：{safari_path} (注意: 这是一个嵌入 PNG 的 SVG)")

    print("完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法：python scripts/generate_favicons.py <图片路径>")
    else:
        generate_icons(sys.argv[1])
