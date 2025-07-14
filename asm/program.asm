[bits 16]
[org 0x0000]  ; �������ص� 0x2000:0x0000 (�����ַ 0x20000)

start:
    ; ���öμĴ���
    mov ax, cs
    mov ds, ax
    mov es, ax

    ; �л���320x200 256ɫģʽ
    mov ax, 0x0013
    int 0x10

    ; ���Ʋ�ɫ����
    mov ax, 0xA000
    mov es, ax
    xor di, di
    mov cx, 64000
    mov al, 0  ; ��ʼ��ɫ

.draw_loop:
    stosb       ; д������
    inc al      ; �ı���ɫ
    loop .draw_loop

    ; �л����ı�ģʽ
    mov ax, 0x0003
    int 0x10

    ; ��ӡ�ɹ���Ϣ
    mov si, success_msg
    call print_string

    ; ��ӡ�ڴ���Ϣ
    mov si, mem_info_msg
    call print_string
    mov ax, cs
    call print_hex_word
    mov si, colon
    call print_string
    mov ax, 0x0000
    call print_hex_word

    ; ����
    cli
    hlt

; ��������
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

; ������
success_msg db 0x0D, 0x0A, "Program successfully loaded and executed! (^_^),Project repo: https://github.com/YunChenqwq/MBRVideo", 0x0D, 0x0A, 0
mem_info_msg db "Running at CS:IP ", 0
colon db ":", 0

; ���ʣ��ռ䣨��ѡ��
times 512-($-$$) db 0