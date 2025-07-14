#by yunchenqwq ai写的cuda加速
import cv2
import numpy as np
from tqdm import tqdm
import numba
from numba import cuda

#vga色表
HUE_MAP = {
    4: 0, 68: 1, 132: 2, 196: 3, 260: 4, 259: 5, 258: 6, 257: 7,
    256: 8, 264: 9, 272: 10, 280: 11, 288: 12, 224: 13, 160: 14,
    96: 15, 32: 16, 33: 17, 34: 18, 35: 19, 36: 20, 28: 21, 20: 22,
    12: 23
}
hue_map_keys = np.array(list(HUE_MAP.keys()), dtype=np.int32)
hue_map_values = np.array(list(HUE_MAP.values()), dtype=np.uint8)
d_hue_map_keys = cuda.to_device(hue_map_keys)
d_hue_map_values = cuda.to_device(hue_map_values)

@cuda.jit(device=True)
def device_rgb_to_vga256(r, g, b, hue_map_keys, hue_map_values):
    """RGB到VGA256颜色转换"""
    min_val = min(r, g, b)
    max_val = max(r, g, b)
    delta = max_val - min_val
    
    if delta <= 10:
        return 16 + ((r + g * 2 + b) // 4) * 16 // 256
    elif delta >= 224:
        key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))

        for i in range(len(hue_map_keys)):
            if hue_map_keys[i] == key:
                return 32 + hue_map_values[i]
        return 32
    elif delta >= 144:
        if min_val >= 85:
            return 8 + round((r-min_val)/delta*2)*4 + round((g-min_val)/delta*2)*2 + round((b-min_val)/delta*2)
        else:
            return 0 + round((r-min_val)/delta*2)*4 + round((g-min_val)/delta*2)*2 + round((b-min_val)/delta*2)
    elif delta >= 91:
        if min_val >= 113:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 56 + hue_map_values[i]
            return 56
        else:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 104 + hue_map_values[i]
            return 104
    elif delta > 40:
        if min_val >= 149:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 80 + hue_map_values[i]
            return 80
        elif min_val >= 57:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 128 + hue_map_values[i]
            return 128
        else:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 176 + hue_map_values[i]
            return 176
    else:
        if min_val >= 113:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256
        elif min_val >= 81:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 152 + hue_map_values[i]
            return 152
        elif min_val >= 65:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256
        elif min_val >= 45:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 224 + hue_map_values[i]
            return 224
        elif min_val >= 32:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            for i in range(len(hue_map_keys)):
                if hue_map_keys[i] == key:
                    return 200 + hue_map_values[i]
            return 200
        else:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256

@cuda.jit
def process_frame_kernel(rgb_frame, output_frame, hue_map_keys, hue_map_values):
    """处理帧"""
    x, y = cuda.grid(2)
    if x < rgb_frame.shape[1] and y < rgb_frame.shape[0]:
        r = rgb_frame[y, x, 0]
        g = rgb_frame[y, x, 1]
        b = rgb_frame[y, x, 2]
        output_frame[y, x] = device_rgb_to_vga256(r, g, b, hue_map_keys, hue_map_values)

def resize_with_aspect_ratio(image, target_width, target_height):
    """保持宽高比调整大小，不足部分填充黑色"""
    h, w = image.shape[:2]
    target_ratio = target_width / target_height
    image_ratio = w / h
    
    if image_ratio > target_ratio:
        new_w = target_width
        new_h = int(target_width / image_ratio)
    else:
        new_h = target_height
        new_w = int(target_height * image_ratio)
    
    # 调整大小
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    
    # 创建黑色背景
    result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # 计算放置位置
    y_offset = (target_height - new_h) // 2
    x_offset = (target_width - new_w) // 2
    
    result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return result

def process_video(input_path, output_path="output.bin", resize_mode="stretch"):
    """
    参数:
        input_path: 输入视频路径
        output_path: 输出文件路径
        resize_mode: 调整大小模式
            "stretch" - 比例拉伸 (默认)
            "keep_aspect" - 保持宽高比，填充黑色
    """
    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    with open(output_path, 'wb') as f:
        for _ in tqdm(range(total_frames), desc="Processing frames"):
            ret, frame = cap.read()
            if not ret:
                break
                
            # 根据模式调整大小
            if resize_mode == "keep_aspect":
                resized = resize_with_aspect_ratio(frame, 320, 200)
            else:  # 默认是stretch模式
                resized = cv2.resize(frame, (320, 200), interpolation=cv2.INTER_NEAREST)
            
            # BGR转RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # 准备CUDA处理
            d_rgb = cuda.to_device(rgb)
            d_output = cuda.device_array((200, 320), dtype=np.uint8)
            
            # 定义块和网格大小
            threadsperblock = (16, 16)
            blockspergrid_x = (rgb.shape[1] + threadsperblock[0] - 1) // threadsperblock[0]
            blockspergrid_y = (rgb.shape[0] + threadsperblock[1] - 1) // threadsperblock[1]
            blockspergrid = (blockspergrid_x, blockspergrid_y)
            
            # 启动核函数
            process_frame_kernel[blockspergrid, threadsperblock](
                d_rgb, d_output, d_hue_map_keys, d_hue_map_values)
            
            # 将结果复制回主机
            vga_frame = d_output.copy_to_host()
            
            f.write(vga_frame.tobytes())
        
        end_frame = np.zeros(64000, dtype=np.uint8)
        f.write(end_frame.tobytes())
        watermark_hex = [0x79, 0x75, 0x6E, 0x63, 0x68, 0x65, 0x6E, 0x71, 0x77, 0x71]
        f.write(bytes(watermark_hex))

    cap.release()
    print(f"Conversion complete. Output: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input video path")
    parser.add_argument("-o", "--output", default="output.bin", help="Output file path")
    parser.add_argument("-m", "--mode", choices=["stretch", "keep_aspect"], 
                       default="stretch", help="Resize mode: stretch (default) or keep_aspect")
    args = parser.parse_args()
    process_video(args.input, args.output, args.mode)