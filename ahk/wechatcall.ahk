; This file contains all the short cuts that I want during the usage of my stupid computer
;#NoTrayIcon 
info .= %0%
; msgbox %info%

; msgbox "hello"

IfWinExist, WeChat
{
    WinActivate, WeChat
    Sleep, 50
    Send ^f
    Sleep, 50
    Send bbsang
    Sleep, 300
    Send {Enter}
}
else
{
    MsgBox "Wechat not opened"
}

;Sleep, 50
;Send autohotkeyauto
;Sleep, 50
;Send {Enter}
