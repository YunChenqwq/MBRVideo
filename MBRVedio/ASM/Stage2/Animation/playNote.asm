lastIntroNote equ song+26*2
lastNote      equ message

soundIndex dw song
soundWait  db 0

playNote:

    mov si, [soundIndex]

    cmp si, lastNote
    jb .nextNote

    ; 回到开头
    mov si, lastIntroNote

    .nextNote:
    dec byte [soundWait]
    cmp byte [soundWait], -1
    jne .end

    lodsw
    mov cx, ax
    and ah, 00011111b

    ; 设置频率
    out 0x42, al
    mov al, ah
    out 0x42, al

    shr ch, 5
    mov [soundWait], ch

    mov [soundIndex], si

    .end: ret
