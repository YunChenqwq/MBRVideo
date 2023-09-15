use16
org 0x7c00

; 设置 CPU

; 修正 CS
jmp 0x0000:correct_cs
correct_cs:

; 设置堆栈
cli                ; 禁用中断
xor ax, ax         ; 将寄存器 AX 清零
mov ss, ax         ; 将 SS 寄存器设置为 0
mov sp, 0x7BF0     ; 设置堆栈指针 SP
sti                ; 允许中断

%include "decompress.asm" ; 解压缩代码和数据

; 准备 CPU 段寄存器

mov ax, 0x2000
mov ds, ax
mov es, ax

jmp 0x2000:0x0000         ; 跳转至解压缩后的数据，启动实际的内核

; 引导扇区签名
times 510 - ($ - $$) db 0
dw 0xAA55

; 包含压缩数据
comp:     incbin "../../Build/stage2-compressed.bin" ; 压缩数据文件路径
compsize: equ $-comp

; 对齐到扇区
times 4096 - ($ - $$) db 0