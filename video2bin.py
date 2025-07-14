#by yunchenqwq
import cv2
import numpy as np
from tqdm import tqdm

#vga色表
HUE_MAP = {
    4: 0, 68: 1, 132: 2, 196: 3, 260: 4, 259: 5, 258: 6, 257: 7,
    256: 8, 264: 9, 272: 10, 280: 11, 288: 12, 224: 13, 160: 14,
    96: 15, 32: 16, 33: 17, 34: 18, 35: 19, 36: 20, 28: 21, 20: 22,
    12: 23
}

def rgb_to_vga256(r, g, b):
    min_val = min(r, g, b)
    max_val = max(r, g, b)
    delta = max_val - min_val
    
    if delta <= 10:
        return 16 + ((r + g * 2 + b) // 4) * 16 // 256
    elif delta >= 224:
        key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
        return 32 + HUE_MAP.get(key, 0)
    elif delta >= 144:
        if min_val >= 85:
            return 8 + round((r-min_val)/delta*2)*4 + round((g-min_val)/delta*2)*2 + round((b-min_val)/delta*2)
        else:
            return 0 + round((r-min_val)/delta*2)*4 + round((g-min_val)/delta*2)*2 + round((b-min_val)/delta*2)
    elif delta >= 91:
        if min_val >= 113:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 56 + HUE_MAP.get(key, 0)
        else:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 104 + HUE_MAP.get(key, 0)
    elif delta > 40:
        if min_val >= 149:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 80 + HUE_MAP.get(key, 0)
        elif min_val >= 57:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 128 + HUE_MAP.get(key, 0)
        else:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 176 + HUE_MAP.get(key, 0)
    else:
        if min_val >= 113:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256
        elif min_val >= 81:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 152 + HUE_MAP.get(key, 0)
        elif min_val >= 65:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256
        elif min_val >= 45:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 224 + HUE_MAP.get(key, 0)
        elif min_val >= 32:
            key = int(round((r-min_val)/delta*4)*64 + round((g-min_val)/delta*4)*8 + round((b-min_val)/delta*4))
            return 200 + HUE_MAP.get(key, 0)
        else:
            return 16 + ((r + g * 2 + b) // 4) * 16 // 256

def resize_with_aspect(image, target_width, target_height, mode="stretch"):
    """
    参数:
        input_path: 输入视频路径
        output_path: 输出文件路径
        resize_mode: 调整大小模式
            "stretch" - 比例拉伸 (默认)
            "keep_aspect" - 保持宽高比，填充黑色
    """
    if mode == "stretch":
        # 直接拉伸到目标尺寸
        return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_NEAREST)
    elif mode == "maintain":
        # 保持宽高比，填充黑色
        h, w = image.shape[:2]
        target_ratio = target_width / target_height
        image_ratio = w / h
        
        if image_ratio > target_ratio:
            new_w = target_width
            new_h = int(target_width / image_ratio)
        else:
            new_h = target_height
            new_w = int(target_height * image_ratio)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
       
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        y_offset = (target_height - new_h) // 2
        x_offset = (target_width - new_w) // 2
        
        result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return result
    else:
        raise ValueError(f"Unknown resize mode: {mode}")

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
                
            resized = resize_with_aspect(frame, 320, 200, resize_mode)
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            vga_frame = np.zeros((200, 320), dtype=np.uint8)
            
            for y in range(200):
                for x in range(320):
                    r, g, b = rgb[y, x]
                    vga_frame[y, x] = rgb_to_vga256(r, g, b)
            
            f.write(vga_frame.tobytes())
        
        # 写入结束帧 (第一个字节为0)
        end_frame = np.zeros(64000, dtype=np.uint8)
        f.write(end_frame.tobytes())

    cap.release()
    print(f"Conversion complete. Output: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input video path")
    parser.add_argument("-o", "--output", default="output.bin", help="Output file path")
    parser.add_argument("-m", "--mode", choices=["stretch", "maintain"], 
                       default="stretch", help="Resize mode: 'stretch' (default) or 'maintain' aspect ratio")
    args = parser.parse_args()
    process_video(args.input, args.output, args.mode)