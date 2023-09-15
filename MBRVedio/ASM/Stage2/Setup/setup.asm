; 设置视频模式
mov ax, 0x0003
int 10h

; 禁用屏幕闪烁（需要EGA显示器）
mov ax, 0x1003
mov bl, 0
int 10h

; 设置主计时器
mov al, 00110100b
out 0x43, al

call setTimer


; 设置中断
cli ; 禁用中断

; 设置定时器中断处理程序
setupInterrupt 0, timerHandler

; 设置键盘中断处理程序
setupInterrupt 1, keyboardHandler

sti ; 再次启用中断


; 设置PC喇叭
; 设置PC喇叭定时器
mov al, 10110110b
out 0x43, al

; 设置默认频率
mov ax, 1193 ; ~1000 Hz
out 0x42, al
mov al, ah
out 0x42, al

; 启用PC喇叭
in al, 61h
or al, 00000011b
out 61h, al


; 调用动画程序
call initDrawing
