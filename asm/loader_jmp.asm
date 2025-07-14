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

    ; Initialize music DAP (9 sectors: LBA 1-9)
    mov byte [music_dap], 0x10
    mov byte [music_dap+1], 0
    mov word [music_dap+2], 1
    mov word [music_dap+4], 0
    mov word [music_dap+6], 0x07E0
    mov dword [music_dap+8], 1
    mov dword [music_dap+12], 0

    ; Initialize video DAP (125 sectors: LBA 11-135)
    mov byte [video_dap], 0x10
    mov byte [video_dap+1], 0
    mov word [video_dap+2], 125
    mov word [video_dap+4], 0
    mov word [video_dap+6], 0x800
    mov dword [video_dap+8], 11
    mov dword [video_dap+12], 0

    ; Initialize music pointers
    mov word [current_ptr], 0x7E00
    mov word [buffer_end], 0x7E00 + 512
    mov word [sectors_remaining], 9
    call load_next_sector

.main_loop:
    mov si, [current_ptr]
    cmp si, [buffer_end]
    jae .load_next_chunk

    mov bx, [si]
    cmp bx, -1
    je .reset_music
    test bx, bx
    jz .silent_note

    call set_frequency
    jmp .play_note

.silent_note:
    in al, 0x61
    and al, 0xFC
    out 0x61, al

.play_note:
    mov ax, [si + 2]
    mov [note_delay], ax
.note_delay_loop:
    call check_video_frame
    call delay_1ms
    dec word [note_delay]
    jnz .note_delay_loop

    in al, 0x61
    and al, 0xFC
    out 0x61, al

    add word [current_ptr], 4
    jmp .main_loop

.load_next_chunk:
    cmp word [sectors_remaining], 0
    jbe .reset_music
    call load_next_sector
    jmp .main_loop

.reset_music:
    mov dword [music_dap+8], 1
    mov word [sectors_remaining], 9
    call load_next_sector
    jmp .main_loop

load_next_sector:
    pusha
    mov ah, 0x42
    mov dl, 0x80
    mov si, music_dap
    int 0x13

    mov word [current_ptr], 0x7E00
    mov word [buffer_end], 0x7E00 + 512
    
    mov eax, [music_dap+8]
    inc eax
    mov [music_dap+8], eax
    
    dec word [sectors_remaining]
    popa
    ret

set_frequency:
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

    mov ax, 0x800
    mov ds, ax
    xor si, si
    mov ax, 0xa000
    mov es, ax
    xor di, di
    mov cx, 64000/2
    rep movsw

    cmp byte [ds:0], 0
    je .video_end
    
    xor ax, ax
    mov ds, ax
    mov eax, [video_dap+8]
    add eax, 125
    mov [video_dap+8], eax
    pop ds
    popa
    ret

.video_end:
    ; 1. Reset disk controller
    mov dl, 0x80
    int 0x13
	mov al, 0xB6
    out 0x43, al
    xor al, al
    out 0x42, al
    ; 关闭扬声器
    in al, 0x61
    and al, 0xFC
    out 0x61, al
    
    ; 2. Restore text mode
    mov ax, 0x0003
    int 0x10
    
    ; 3. Load program using CHS (more reliable)
    mov ax, 0x0201      ; AH=02(read), AL=1(sector count)
    mov cx, 0x000B      ; CH=0(cylinder 0), CL=11(sector 11)
    mov dx, 0x0080      ; DH=0(head 0), DL=80h(first HDD)
    mov bx, 0x2000      ; ES:BX = 0x2000:0
    mov es, bx
    xor bx, bx
    int 0x13
    
    ; 4. Setup environment and jump
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov sp, 0xFFFE
    
    ; Jump to loaded program
    jmp 0x2000:0x0000

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

; Data section
current_ptr dw 0
buffer_end dw 0
note_delay dw 0
video_timer db 0
sectors_remaining dw 9

music_dap:
    db 0x10, 0
    dw 1
    dw 0, 0x07E0
    dq 1
    dq 0

video_dap:
    db 0x10, 0
    dw 125
    dw 0, 0x800
    dq 11
    dq 0

times 510-($-$$) db 0
dw 0xAA55

; ===== Included data =====
%include "middata.asm"      ; Music data (sectors 2-10)
times 4608 - ($ - music_data) db 0
incbin "program.bin"        ; Program to load (sector 11)
times 5120 - ($ - music_data) db 0