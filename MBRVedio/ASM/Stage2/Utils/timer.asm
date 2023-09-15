defaultClock equ 11932 ; ~100 Hz
currentClock dw defaultClock

; 更新当前计时器的值
setTimer:
    mov ax, [currentClock]
    out 0x40, al
    mov al, ah
    out 0x40, al
    
    ret

maxClock equ defaultClock/6
minClock equ defaultClock*3

; 加速计时器使用以下公式计算：
; currentClock = currentClock * clockPreMul / clockDiv
clockPreMul  equ 2
clockDiv     equ 3

; 加速当前计时器
speedUp:
    mov ax, [currentClock]
    
    mov bx, clockPreMul
    mul bx
    
    mov bx, clockDiv
    div bx
    
    cmp ax, maxClock
    ja .resetTimer
    
    ; 如果速度过快，则将计时器重置为最小速度
    mov ax, minClock
    
    .resetTimer:
        mov [currentClock], ax
        call setTimer
    
    ret
