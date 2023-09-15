import sys
import math
import struct
import os
from PIL import Image

# DOS调色板颜色表
doscolors = [
    (0x00, 0x00, 0x00),  # 0
    (0x00, 0x00, 0xa8),  # 1
    (0x00, 0xa8, 0x00),  # 2
    (0x00, 0xa8, 0xa8),  # 3
    (0xa8, 0x00, 0x00),  # 4
    (0xa8, 0x00, 0xa8),  # 5
    (0xa8, 0xa8, 0x00),  # 6
    (0xa8, 0xa8, 0xa8),  # 7
    (0x54, 0x54, 0x54),  # 8
    (0x54, 0x54, 0xff),  # 9
    (0x54, 0xff, 0x54),  # 10
    (0x54, 0xff, 0xff),  # 11
    (0xff, 0x54, 0x54),  # 12
    (0xff, 0x54, 0xff),  # 13
    (0xff, 0xff, 0x54),  # 14
    (0xff, 0xff, 0xff)  # 15
]


def color_distance(a, b):
    # 计算两个颜色之间的距离
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def nearest_color(color):
    nearest = 0

    for i in range(len(doscolors)):
        # 找到最接近的DOS调色板颜色
        if color_distance(color, doscolors[i]) < color_distance(color, doscolors[nearest]):
            nearest = i

    return nearest


buf = b""

for imgf in os.listdir("ImageOut"):
    if imgf.endswith(".png"):
        img = Image.open(os.path.join("ImageOut", imgf)).convert("RGB")
        w, h = img.size

        for y in range(0, h, 2):
            for x in range(w):
                # 将每个像素转换为最接近的DOS调色板颜色，并将结果保存为字节
                b = (nearest_color(img.getpixel((x, y))) << 4) | nearest_color(img.getpixel((x, y + 1)))
                buf += struct.pack("B", b)

        img.close()

with open("Image.bin", "wb") as out:
    # 将转换后的二进制数据写入到文件中
    out.write(buf)
    print("图像bin文件生成生成成功（●＞ω＜●）")