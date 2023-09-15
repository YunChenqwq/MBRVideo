import os
from PIL import Image

def convert_images_to_80x50(folder_path):
    # 创建输出文件夹
    output_folder = 'ImageOut'
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 确保文件是图片
        if filename.endswith(('.jpg', '.jpeg', '.bmp','.png')):
            # 获取文件的绝对路径
            filepath = os.path.join(folder_path, filename)
            
            # 打开图片
            try:
                image = Image.open(filepath)
            except IOError:
                print(f"无法打开文件: {filepath}")
                continue
            
            # 确保图片模式为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为80x50大小
            image = image.resize((80, 50), resample=Image.LANCZOS)
            
            # 转换为24色位图 后期检查时发现是没必要的操作
            image = image.quantize(colors=24)
            
            # 将图片保存为png格式
            new_filename = os.path.splitext(filename)[0] + '.png'
            new_filepath = os.path.join(output_folder, new_filename)
            image.save(new_filepath, 'PNG')
            
           # print(f"已将{filename}转换为{new_filename}")

# 调用函数将input文件夹中的图片转换为80x50大小，并转换为24色位图后输出到imgout文件夹
convert_images_to_80x50('Input')
print("文件尺寸调整完成（＾∀＾）")