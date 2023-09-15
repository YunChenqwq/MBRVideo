import os

print("tips：如果你使用的不是ScreenTogif提取的图片而是自己整理的素材命名，请忽略掉报错信息并保证文件顺序正确性(*′▽‘*),将图片文件直接拷贝到ImageOut中")

# 指定文件夹路径
folder_path = "input"

# 获取文件夹中的所有文件
files = os.listdir(folder_path)

# 提取指定扩展名的文件
valid_extensions = ['.jpg', '.jpeg', '.bmp', '.png']
files = [file for file in files if os.path.splitext(file)[-1].lower() in valid_extensions]

# 提取排序序号
file_info = [(int(file.split()[0]), file) for file in files]

# 按照排序序号进行排序
file_info.sort(key=lambda x: x[0])

count = 1

# 遍历文件
for _, file_name in file_info:
    # 获取文件扩展名
    ext = os.path.splitext(file_name)[-1]
    # 构建新文件名
    new_name = str(count) + ext
    old_path = os.path.join(folder_path, file_name)
    new_path = os.path.join(folder_path, new_name)
    # 重命名文件
    os.rename(old_path, new_path)
    # 打印提示信息
    # print(f"将文件 {file_name} 重命名为 {new_name}")

    # 自增序号
    count += 1

print("文件重命名完成（＾∀＾）")
