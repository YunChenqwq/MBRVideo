drawIntroFrame:
    push es
    push 0xb800
    pop es
    
    ; 增加帧计数器的值，使得引导动画运行得更快
    mov byte [frameTickCounter], 5

    ; 检查消息是否已经完全显示
    cmp si, messageLength
    jae .end

    mov di, si
    imul di, 2

    mov byte al, [si+message]

    mov byte [es:di], al
    mov byte [es:di+1], 0xf0

    inc si
    mov [frameIndex], si

    .end:
        pop es
        ret
