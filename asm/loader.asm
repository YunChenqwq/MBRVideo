;by yunchenqwq
[bits 16]
[org 0x7c00]
cpu 386

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00

    mov ax, 0x0013
    int 0x10

    ;初始化音乐DAP
    mov byte [music_dap], 0x10
    mov byte [music_dap+1], 0
    mov word [music_dap+2], 1         
    mov word [music_dap+4], 0          ; 偏移量(0x7E00)
    mov word [music_dap+6], 0x07E0     ; 段地址(0x07E0:0x0000 = 0x7E00)
    mov dword [music_dap+8], 1         ; 起始LBA=1
    mov dword [music_dap+12], 0

    ;初始化视频DAP
    mov byte [video_dap], 0x10
    mov byte [video_dap+1], 0
    mov word [video_dap+2], 125       ; 125扇区
    mov word [video_dap+4], 0          ; 位
    mov word [video_dap+6], 0x800      
    mov dword [video_dap+8], 11        
    mov dword [video_dap+12], 0

    ; 初始化音乐指针
    mov word [current_ptr], 0x7E00
    mov word [buffer_end], 0x7E00 + 512
    mov word [sectors_remaining], 10   
    call load_next_sector

.main_loop:
    ; 边界检查
    mov si, [current_ptr]
    cmp si, [buffer_end]
    jae .load_next_chunk

    ; 读取频率和时间(每个音符4字节)
    mov bx, [si]       ; 频率
    cmp bx, -1         ; 结束标记
    je .reset_music
    test bx, bx        ; 检查是否为0
    jz .silent_note

    call set_frequency ; 设置扬声器频率
    jmp .play_note

.silent_note:
    ; 静音处理
    in al, 0x61
    and al, 0xFC
    out 0x61, al

.play_note:
    mov ax, [si + 2]   ; 时间(毫秒)
    mov [note_delay], ax

.note_delay_loop:
    call check_video_frame
    call delay_1ms
    dec word [note_delay]
    jnz .note_delay_loop

    ; 关闭扬声器
    in al, 0x61
    and al, 0xFC
    out 0x61, al

    ; 更新指针(每个音符4字节)
    add word [current_ptr], 4
    jmp .main_loop

.load_next_chunk:
    ; 检查是否还有数据要读取
    cmp word [sectors_remaining], 0
    jbe .reset_music
    call load_next_sector
    jmp .main_loop

.reset_music:
    ; 重置音乐循环
    mov dword [music_dap+8], 1        ; 重置LBA
    mov word [sectors_remaining], 10  ; 重置剩余扇区数
    call load_next_sector
    jmp .main_loop

load_next_sector:
    pusha
    mov ah, 0x42
    mov dl, 0x80
    mov si, music_dap
    int 0x13
    jc disk_error

    ; 更新指针和计数器
    mov word [current_ptr], 0x7E00
    mov word [buffer_end], 0x7E00 + 512
    
    ; 更新DAP
    mov eax, [music_dap+8]
    inc eax
    mov [music_dap+8], eax
    
    dec word [sectors_remaining]
    popa
    ret

set_frequency:  ; (BX=频率Hz)
    push ax
    push dx
    mov al, 0xB6
    out 0x43, al
    mov dx, 0x12
    mov ax, 0x34DC
    div bx
    out 0x42, al
    mov al, ah
    out 0x42, al
    in al, 0x61
    or al, 0x03
    out 0x61, al
    pop dx
    pop ax
    ret

check_video_frame:
    push ax
    inc byte [video_timer]
    cmp byte [video_timer], 20
    jb .skip
    mov byte [video_timer], 0
    call load_video_frame
.skip:
    pop ax
    ret

load_video_frame:
    pusha
    push ds
    xor ax, ax
    mov ds, ax
    mov si, video_dap
    mov ah, 0x42 
    mov dl, 0x80
    int 0x13
    jc disk_error

    ; 复制帧数据到显存
    mov ax, 0x800
    mov ds, ax
    xor si, si
    mov ax, 0xa000
    mov es, ax
    xor di, di
    mov cx, 64000/2
    rep movsw

    ; 检查视频结束
    cmp byte [ds:0], 0
    je .video_end
    
    ; 更新LBA
    xor ax, ax
    mov ds, ax
    mov eax, [video_dap+8]
    add eax, 125
    mov [video_dap+8], eax
    pop ds
    popa
    ret

.video_end:
    ; 重置视频LBA
    xor ax, ax
    mov ds, ax
    mov dword [video_dap+8], 11
    pop ds
    popa
    ret

delay_1ms:
    push cx
    push dx
    mov cx, 0x0000
    mov dx, 0x03E8
    mov ah, 0x86
    int 0x15
    pop dx
    pop cx
    ret

disk_error:
    mov si, error_msg
    call print_string
    cli
    hlt

print_string:
    push ax
    push si
.loop:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp .loop
.done:
    pop si
    pop ax
    ret

;数据区
error_msg db "Disk error!", 0
current_ptr dw 0
buffer_end dw 0
note_delay dw 0
video_timer db 0
sectors_remaining dw 0

music_dap:
    db 0x10, 0
    dw 1
    dw 0, 0x07E0    ; 缓冲区地址0x7E00
    dq 1
    dq 0

video_dap:
    db 0x10, 0
    dw 125
    dw 0, 0x800
    dq 11
    dq 0
; 确保引导扇区正好512字节
times 510-($-$$) db 0
dw 0xAA55


%include "middata.asm"
times 5120 - ($ - music_data) db 0