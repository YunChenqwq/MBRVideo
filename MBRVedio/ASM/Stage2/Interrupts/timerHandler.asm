frameTickCounter db 0
noteTickCounter  db 0
nyanTickCounter  db 0

%macro onTimer 3
    inc byte %1
    cmp byte %1, %2
    jne %%checkNext

    mov byte %1, 0

    call %3

    %%checkNext:
%endmacro

timerHandler:
    startInterrupt

    onTimer [frameTickCounter],  8, displayFrame ; 每 8 个计时周期调用 displayFrame 函数
    onTimer [noteTickCounter],  12, playNote ; 每 12 个计时周期调用 playNote 函数
    onTimer [nyanTickCounter],  10, countNyan ; 每 10 个计时周期调用 countNyan 函数

    finishInterrupt
