cli ; 禁用中断

; 设置定时器中断处理程序
setupInterrupt 0, timerHandler

; 设置键盘中断处理程序
setupInterrupt 1, keyboardHandler

sti ; 再次启用中断
