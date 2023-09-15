%macro onKey 2
    cmp al, %1
    jne %%notPressed
    
    call %2
    
    %%notPressed:
%endmacro

keyboardHandler:
    startInterrupt

    in al, 60h ; 读取键盘状态

    onKey 0x1F, speedUp ; 当按下S键时加速主计时器

    finishInterrupt
