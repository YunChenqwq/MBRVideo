# MBRvideo Builder Tool v2.0

一个用于生成在实模式下MBR视频的工具，可一键生成GIF/MP4格式的MBR视频，同时加入MIDI音乐,操作简单，只要会动脑有手都能使用。注释详细，请注意VGA调色板只有256色，色彩效果可能不太理想。
整合包蓝奏云链接https://wwya.lanzoue.com/iNyRh314r1yb 密码:4naq
QQ群：653488716

## 🖥 功能简介
- 🎥 视频输入支持 `.mp4` / `.avi` 等格式，并可选择拉伸或保持宽高比处理方式
- 🎼 可选 MIDI 音乐输入，支持速度/音调调整，转换为 ASM 格式
- 💿 支持两种引导模式：
  - `loop`：视频循环播放
  - `jump`：视频播放完后跳转到自己的bootloader（如何加入自己的bootloader详见下文）
- ⚡ 支持 CUDA 加速的视频处理（处理速度提升50倍，1秒/帧→0.02秒/帧）
- 📦 自动构建输出 `.img` 镜像
- 🧾 支持导出 HEX 格式数据
- 📜 可视化日志输出，实时显示构建进度和状态

## 📋 参数说明

### 视频设置
| 参数名               | 说明                              | 默认值       |
|----------------------|-----------------------------------|-------------|
| Video Input          | 视频输入路径                      | 必填        |
| Video Output         | 输出 `.bin` 文件名（不含路径）     | output_video.bin |
| Video Mode           | 拉伸 (`stretch`) 或保留比例，直接用黑边填充 (`keep_aspect`) | keep_aspect |
| Enable CUDA          | 是否启用 CUDA 加速                | False       |

### MIDI 设置（可选）
| 参数名              | 说明                          | 默认值     |
|---------------------|-----------------------------|-----------|
| MIDI Input          | MIDI 文件路径（`.mid` 或 `.midi`）| 空        |
| Playback Speed      | 播放速度（1.0=正常速度，但是实测有点偏慢）       | 1.0       |
| Pitch Adjustment    | 移调（单位：半音）             | 0         |
| ASM Output File     | 生成的 ASM 数据文件名          | music.asm |

### 引导程序设置
| 参数名              | 说明                     | 默认值    |
|---------------------|------------------------|----------|
| Bootloader Type     | `loop` 或 `jump` 模式   | loop     |
| Bootloader Binary   | 输出 bootloader 文件名  | loader.bin |

### 镜像设置
| 参数名             | 说明                    | 默认值     |
|--------------------|-----------------------|-----------|
| Image Output       | 最终生成 `.img` 镜像名称 | yourimg.img |

---

## 🚀 使用方法

### 1. GUI模式（推荐）
1. 双击运行 `run.bat`（整合包内预配置环境）
   - 或直接下载或git clone本仓库后，手动运行 `gui.py`（需已安装依赖）
2. 选择视频文件（必选）和MIDI文件（可选）
3. 配置处理参数：
   - 视频模式（拉伸/保持比例）
   - 是否启用CUDA加速
   - 引导模式（loop/jump）
4. 点击 **Start Build/开始** 按钮
5. 构建完成后可导出HEX数据

📂 **输出文件**（生成于 `build/` 目录）：
- `output_video.bin` - 处理后的视频数据
- `loader.bin` - 编译后的引导程序
- `yourimg.img` - 最终镜像文件

### 2. 命令行模式（已过时）
直接运行 `build.bat`，参数已在批处理文件中预设

---

## 📦 依赖环境
### 基础要求
- Python ≥ 3.8
- 安装依赖：`pip install -r requirements.txt`

### 额外工具
- NASM（用于编译你的bootloader）
- 你自己的脑子

### CUDA支持（可选）
- NVIDIA显卡 + 对应驱动
- CUDA Toolkit 11.0+
- cuDNN 8.0+
- numpy 你都有cuda了还没用过？自己pip

---

## 常见问题解答
1. 汇编错误：TIMES值为负数
**错误信息**：
asm/loader_jmp.asm:237: error: TIMES value -508 is negative
midi文件超出大小限制了，在最新的版本中已经添加了自动截断，但是你如果使用的是jmp模式仍然会触发

2.没装cuda使用cuda模式
2. "C:\Users\admin\Desktop\MBRvideo\Python38\lib\site-packages\numba\cuda\cudadrv\driver.py", line 254, in ensure_initialized
self.cuInit(0)
File "C:\Users\admin\Desktop\MBRvideo\Python38\lib\site-packages\numba\cuda\cudadrv\driver.py", line 327, in safe_cuda_api_call
self._check_ctypes_error(fname, retcode)
File "C:\Users\admin\Desktop\MBRvideo\Python38\lib\site-packages\numba\cuda\cudadrv\driver.py", line 395, in _check_ctypes_error
raise CudaAPIError(retcode, msg)
numba.cuda.cudadrv.driver.CudaAPIError: [100] Call to cuInit results in CUDA_ERROR_NO_DEVICE

## 🔧 高级配置

### 添加自定义Bootloader
1. 准备你的ASM源码文件（如 `yourcode.asm`）
2. 使用NASM编译：`nasm yourcode.asm -o program.bin`
3. 请确保你的程序代码是org 0x0000而不是0X7C00，且其他的东西也需要调整。否则将无法正常运行。详细自己询问ai吧


## 🚀将程序写到到硬盘
1. 确保你的生成文件名为yourimg.img
2. 将文件和write.cpp编译出的exe在同一目录下
3. 运行write.cpp，将自动写入你要写入的设备中
4. 如果你想将镜像写入自己的程序，请参考write.cpp。有两种方式，一是直接将镜像加入资源文件或使用数组装gui导出的hex




## 支持作者（求投喂！！）
写代码真的很累，不想再碰了T-T，请给我买杯可乐咖啡以支持我更新。
 	![image](https://github.com/YunChenqwq/MBRVideo/blob/main/zsm.jpg)
