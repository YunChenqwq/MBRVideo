%macro startInterrupt 0
    pusha ; 保存所有寄存器
%endmacro

%macro finishInterrupt 0
    ; 确认中断
    mov al, 0x20
    out 0x20, al

    popa ; 恢复所有寄存器
    iret ; 从中断返回
%endmacro

%macro setupInterrupt 2
    ; 设置正确的段
    push ds
    push 0x0000
    pop ds

    ; 注册中断处理程序
    mov word [(%1+8)*4], %2  ; 中断处理程序
    mov word [(%1+8)*4+2], 0x2000 ; 段地址 0x2000

    pop ds
%endmacro
