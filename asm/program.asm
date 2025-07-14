[bits 16]
[org 0x0000]  ; 将被加载到 0x2000:0x0000 (物理地址 0x20000)

start:
    ; 设置段寄存器
    mov ax, cs
    mov ds, ax
    mov es, ax

    ; 切换到320x200 256色模式
    mov ax, 0x0013
    int 0x10

    ; 绘制彩色条纹
    mov ax, 0xA000
    mov es, ax
    xor di, di
    mov cx, 64000
    mov al, 0  ; 起始颜色

.draw_loop:
    stosb       ; 写入像素
    inc al      ; 改变颜色
    loop .draw_loop

    ; 切换回文本模式
    mov ax, 0x0003
    int 0x10

    ; 打印成功信息
    mov si, success_msg
    call print_string

    ; 打印内存信息
    mov si, mem_info_msg
    call print_string
    mov ax, cs
    call print_hex_word
    mov si, colon
    call print_string
    mov ax, 0x0000
    call print_hex_word

    ; 挂起
    cli
    hlt

; 辅助函数
print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

print_hex_word:
    push ax
    mov al, ah
    call print_hex_byte
    pop ax
    call print_hex_byte
    ret

print_hex_byte:
    push ax
    shr al, 4
    call .nibble_to_hex
    pop ax
    and al, 0x0F
    call .nibble_to_hex
    ret
.nibble_to_hex:
    cmp al, 9
    jbe .digit
    add al, 7
.digit:
    add al, '0'
    mov ah, 0x0E
    int 0x10
    ret

; 数据区
success_msg db 0x0D, 0x0A, "Program successfully loaded and executed! (^_^),Project repo: https://github.com/YunChenqwq/MBRVideo", 0x0D, 0x0A, 0
mem_info_msg db "Running at CS:IP ", 0
colon db ":", 0

; 填充剩余空间（可选）
times 512-($-$$) db 0