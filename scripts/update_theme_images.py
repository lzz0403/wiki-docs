import os
import sys
import base64
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image

def resize_and_pad(img, target_size, fill_color=(0, 0, 0, 0)):
    """
    将图片调整为目标尺寸，保持纵横比，居中，多余部分填充透明或指定颜色。
    """
    target_w, target_h = target_size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h

    if img_ratio > target_ratio:
        # 图片更宽，以宽度为基准
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        # 图片更高，以高度为基准
        new_h = target_h
        new_w = int(target_h * img_ratio)

    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    new_img = Image.new("RGBA", target_size, fill_color)
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    
    new_img.paste(resized_img, (paste_x, paste_y))
    return new_img

def get_svg_size(svg_path):
    """
    尝试从 SVG 文件中解析 width 和 height。
    如果失败，返回默认值 (512, 512)。
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        width = root.get('width')
        height = root.get('height')
        
        if width and height:
            # 简单的单位处理，去掉 px, pt 等
            w = int(float(width.replace('px', '').replace('pt', '')))
            h = int(float(height.replace('px', '').replace('pt', '')))
            return (w, h)
            
        # 如果没有宽高，尝试看 viewBox
        viewbox = root.get('viewBox')
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                return (int(float(parts[2])), int(float(parts[3])))
                
    except Exception as e:
        print(f"解析 SVG 尺寸失败 {svg_path}: {e}")
    
    return (512, 512) # 默认回退尺寸

def update_theme_images(source_path, target_dir="../theme/assets/images"):
    if not os.path.exists(source_path):
        print(f"错误：找不到源图片 {source_path}")
        return

    if not os.path.exists(target_dir):
        print(f"错误：找不到目标目录 {target_dir}")
        return

    try:
        src_img = Image.open(source_path)
    except Exception as e:
        print(f"无法打开源图片：{e}")
        return

    print(f"开始使用 {source_path} 更新 {target_dir} 下的图片...")

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        if not os.path.isfile(file_path):
            continue

        lower_name = filename.lower()
        
        # 处理位图 (PNG, JPG, WEBP)
        if lower_name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            try:
                with Image.open(file_path) as target_img:
                    target_size = target_img.size
                
                print(f"处理 {filename} (目标尺寸: {target_size})...")
                new_img = resize_and_pad(src_img, target_size)
                new_img.save(file_path)
                
            except Exception as e:
                print(f"处理 {filename} 失败: {e}")

        # 处理 SVG
        elif lower_name.endswith('.svg'):
            try:
                target_size = get_svg_size(file_path)
                print(f"处理 SVG {filename} (解析尺寸: {target_size})...")
                
                new_img = resize_and_pad(src_img, target_size)
                
                # 转 Base64
                buffered = BytesIO()
                new_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # 生成新的 SVG 内容
                svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{target_size[0]}" height="{target_size[1]}" viewBox="0 0 {target_size[0]} {target_size[1]}">
 <image width="100%" height="100%" href="data:image/png;base64,{img_str}" />
</svg>"""
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                    
            except Exception as e:
                print(f"处理 SVG {filename} 失败: {e}")

    print("所有图片更新完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法：python scripts/update_theme_images.py <源图片路径>")
    else:
        update_theme_images(sys.argv[1])
