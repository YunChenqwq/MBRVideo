@echo off
setlocal enabledelayedexpansion

REM ==============================================
REM 构建脚本参数配置区（用户只需修改等号右侧值）
REM ==============================================
set VIDEO_INPUT=input.mp4
set VIDEO_OUTPUT=output_video.bin
set VIDEO_MODE=stretch
set USE_CUDA=1

REM 0=禁用CUDA，1=启用（自行确认环境支持，可提速50倍）

set MIDI_INPUT=input.mid
set MIDI_SPEED=2
set MIDI_OUTPUT=middata.asm

set LOADER_SOURCE=asm\loader.asm
set LOADER_BINARY=loader.bin
set IMG_OUTPUT=yourimg.img

REM ==============================================
echo yunchenqwq MBRvideo
echo 构建开始...
echo 视频输入: %VIDEO_INPUT% [模式: %VIDEO_MODE%]
echo MIDI输入: %MIDI_INPUT% [速度: x%MIDI_SPEED%]
echo CUDA加速: %USE_CUDA%
echo.

REM 创建目录
if not exist "build" mkdir build
if not exist "asm" mkdir asm

REM 检查文件是否存在
if not exist "%VIDEO_INPUT%" (
    echo 错误: 视频文件 [%VIDEO_INPUT%] 不存在
    dir *.mp4 *.avi /b 2>nul || echo 未找到其他视频文件
    pause
    exit /b 1
)

if not exist "%MIDI_INPUT%" (
    echo 错误: MIDI文件 [%MIDI_INPUT%] 不存在
    dir *.mid *.midi /b 2>nul || echo 未找到其他MIDI文件
    pause
    exit /b 1
)

if not exist "%LOADER_SOURCE%" (
    echo 错误: 引导程序 [%LOADER_SOURCE%] 不存在
    pause
    exit /b 1
)

REM 检查基础环境
where python >nul || (echo 错误: 未安装Python & pause & exit /b 1)
where nasm >nul || (echo 错误: 未安装NASM & pause & exit /b 1)

REM 安装Python依赖（静默模式）
echo 正在安装Python依赖...
python -m pip install opencv-python numpy tqdm mido --quiet >nul
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败，请手动运行: python -m pip install opencv-python numpy tqdm mido
    pause
    exit /b 1
)

REM 视频转换（直接使用用户配置的CUDA选项）
echo 正在转换视频...
if "%USE_CUDA%"=="1" (
    python video2bin_cuda.py "%VIDEO_INPUT%" -o "build\%VIDEO_OUTPUT%" -m %VIDEO_MODE%
) else (
    python video2bin.py "%VIDEO_INPUT%" -o "build\%VIDEO_OUTPUT%" -m %VIDEO_MODE%
)
if %errorlevel% neq 0 (
    echo 错误: 视频转换失败
    if "%USE_CUDA%"=="1" echo 提示: 若CUDA不可用，请设置 USE_CUDA=0
    pause
    exit /b 1
)

REM MIDI转换
echo 正在转换MIDI...
python mid2data.py "%MIDI_INPUT%" %MIDI_SPEED%
if %errorlevel% neq 0 (
    echo 错误: MIDI转换失败
    pause
    exit /b 1
)
move "%MIDI_OUTPUT%" asm\ >nul || (echo 错误: 移动MIDI数据失败 & pause & exit /b 1)

REM 编译引导程序
echo 正在编译引导程序...
pushd asm
nasm -f bin loader.asm -o "..\build\%LOADER_BINARY%"
if %errorlevel% neq 0 (
    echo 错误: 编译失败
    popd
    pause
    exit /b 1
)
popd

REM 生成镜像
echo 正在生成最终镜像...
copy /b "build\%LOADER_BINARY%" + "build\%VIDEO_OUTPUT%" "build\%IMG_OUTPUT%" >nul || (
    echo 错误: 镜像合并失败
    pause
    exit /b 1
)

echo.
echo ===== 构建成功 =====
echo 输出文件: build\%IMG_OUTPUT%
echo 视频模式: %VIDEO_MODE%
echo CUDA加速: %USE_CUDA%
echo.
pause
endlocal