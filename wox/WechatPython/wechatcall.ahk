IfWinExist, WeChat
{
    WinActivate, WeChat
    Sleep, 50
    Send ^f
    Sleep, 50
    Send %1%
    Sleep, 50
    Send {LShift}
    Sleep, 50
    Send {LShift}
    Sleep, 300
    Send {Enter}
}
IfWinExist, 微信
{
    WinActivate, 微信
    Sleep, 50
    Send ^f
    Sleep, 50
    Send %1%
    Sleep, 50
    Send {LShift}
    Sleep, 50
    Send {LShift}
    Sleep, 300
    Send {Enter}
}
If !WinExist("WeChat") and !WinExist("微信")
{
    MsgBox "Wechat not opened"
}