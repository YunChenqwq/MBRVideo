frameIndex dw 0

frameSize:  equ (80*50) / 2 ; 一个帧的原始二进制大小
lastFrame:  equ special

displayFrame:
    ; 设置额外段为视频内存
    push es
    push 0xb800
    pop es
    
    mov di, 0

    mov si, [frameIndex]

    cmp word [soundIndex], lastIntroNote
    ja .normalFrame
    jne .introFrame

    ; 当引导动画完成时，重置帧索引
    mov si, frames
    
    ; 恢复消息字符
    mov di, 0
    mov cx, messageLength
    mov ax, 0x00DC
    rep stosw
    
    jmp .normalFrame

    ; 引导动画帧
    .introFrame:
        call drawIntroFrame
        jmp .end

    ; 普通动画帧
    .normalFrame:
        call drawNormalFrame
    
    ; 当到达最后一帧时，重置帧索引
    cmp word [frameIndex], lastFrame
    jb .end
    mov word [frameIndex], frames

    .end:
        pop es
        ret

%include "Animation/Image/initDrawing.asm"
%include "Animation/Image/drawIntroFrame.asm"
%include "Animation/Image/drawNormalFrame.asm"
