import webview
import subprocess
import threading

def start_backend():
    subprocess.Popen(['python', 'main.py'])

if __name__ == '__main__':
    threading.Thread(target=start_backend, daemon=True).start()
    webview.create_window('代码审查系统', 'http://localhost:5173')
    webview.start() 