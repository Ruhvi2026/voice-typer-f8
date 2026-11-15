Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\INDIA\BanglaVoiceTyper"
WshShell.Run """C:\Users\INDIA\AppData\Local\Programs\Python\Python313\pythonw.exe"" ""C:\Users\INDIA\BanglaVoiceTyper\app.py""", 0, False
