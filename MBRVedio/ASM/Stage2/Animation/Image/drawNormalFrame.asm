drawNormalFrame:
    push es
    push 0xb800
    pop es
    
    mov ax, [nyanTimeBin]
    mov dx, 0
    mov bx, 10
    div bx
    
    cmp ax, 420
    jne .displayFrame
    
    ; 在 420 秒时显示特殊图像
    mov si, special
    
    ; 显示帧
    .displayFrame:
        mov di, 1 ; 偏移一个字节
        
        mov cx, frameSize
        .draw:
            lodsb
            stosb
            inc di
        loop .draw
        
        mov [frameIndex], si
        
    .end:
        pop es
        ret
