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
