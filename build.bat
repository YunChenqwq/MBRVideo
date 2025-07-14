@echo off
setlocal enabledelayedexpansion

REM ==============================================
REM �����ű��������������û�ֻ���޸ĵȺ��Ҳ�ֵ��
REM ==============================================
set VIDEO_INPUT=input.mp4
set VIDEO_OUTPUT=output_video.bin
set VIDEO_MODE=stretch
set USE_CUDA=1

REM 0=����CUDA��1=���ã�����ȷ�ϻ���֧�֣�������50����

set MIDI_INPUT=input.mid
set MIDI_SPEED=2
set MIDI_OUTPUT=middata.asm

set LOADER_SOURCE=asm\loader.asm
set LOADER_BINARY=loader.bin
set IMG_OUTPUT=yourimg.img

REM ==============================================
echo yunchenqwq MBRvideo
echo ������ʼ...
echo ��Ƶ����: %VIDEO_INPUT% [ģʽ: %VIDEO_MODE%]
echo MIDI����: %MIDI_INPUT% [�ٶ�: x%MIDI_SPEED%]
echo CUDA����: %USE_CUDA%
echo.

REM ����Ŀ¼
if not exist "build" mkdir build
if not exist "asm" mkdir asm

REM ����ļ��Ƿ����
if not exist "%VIDEO_INPUT%" (
    echo ����: ��Ƶ�ļ� [%VIDEO_INPUT%] ������
    dir *.mp4 *.avi /b 2>nul || echo δ�ҵ�������Ƶ�ļ�
    pause
    exit /b 1
)

if not exist "%MIDI_INPUT%" (
    echo ����: MIDI�ļ� [%MIDI_INPUT%] ������
    dir *.mid *.midi /b 2>nul || echo δ�ҵ�����MIDI�ļ�
    pause
    exit /b 1
)

if not exist "%LOADER_SOURCE%" (
    echo ����: �������� [%LOADER_SOURCE%] ������
    pause
    exit /b 1
)

REM ����������
where python >nul || (echo ����: δ��װPython & pause & exit /b 1)
where nasm >nul || (echo ����: δ��װNASM & pause & exit /b 1)

REM ��װPython��������Ĭģʽ��
echo ���ڰ�װPython����...
python -m pip install opencv-python numpy tqdm mido --quiet >nul
if %errorlevel% neq 0 (
    echo ����: ������װʧ�ܣ����ֶ�����: python -m pip install opencv-python numpy tqdm mido
    pause
    exit /b 1
)

REM ��Ƶת����ֱ��ʹ���û����õ�CUDAѡ�
echo ����ת����Ƶ...
if "%USE_CUDA%"=="1" (
    python video2bin_cuda.py "%VIDEO_INPUT%" -o "build\%VIDEO_OUTPUT%" -m %VIDEO_MODE%
) else (
    python video2bin.py "%VIDEO_INPUT%" -o "build\%VIDEO_OUTPUT%" -m %VIDEO_MODE%
)
if %errorlevel% neq 0 (
    echo ����: ��Ƶת��ʧ��
    if "%USE_CUDA%"=="1" echo ��ʾ: ��CUDA�����ã������� USE_CUDA=0
    pause
    exit /b 1
)

REM MIDIת��
echo ����ת��MIDI...
python mid2data.py "%MIDI_INPUT%" %MIDI_SPEED%
if %errorlevel% neq 0 (
    echo ����: MIDIת��ʧ��
    pause
    exit /b 1
)
move "%MIDI_OUTPUT%" asm\ >nul || (echo ����: �ƶ�MIDI����ʧ�� & pause & exit /b 1)

REM ������������
echo ���ڱ�����������...
pushd asm
nasm -f bin loader.asm -o "..\build\%LOADER_BINARY%"
if %errorlevel% neq 0 (
    echo ����: ����ʧ��
    popd
    pause
    exit /b 1
)
popd

REM ���ɾ���
echo �����������վ���...
copy /b "build\%LOADER_BINARY%" + "build\%VIDEO_OUTPUT%" "build\%IMG_OUTPUT%" >nul || (
    echo ����: ����ϲ�ʧ��
    pause
    exit /b 1
)

echo.
echo ===== �����ɹ� =====
echo ����ļ�: build\%IMG_OUTPUT%
echo ��Ƶģʽ: %VIDEO_MODE%
echo CUDA����: %USE_CUDA%
echo.
pause
endlocal