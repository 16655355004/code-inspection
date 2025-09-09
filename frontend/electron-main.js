const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
let pyProc = null;

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: { nodeIntegration: true }
    });
    win.loadURL('http://localhost:5173');
}

function startPython() {
    pyProc = spawn('python', ['../backend/main.py']);
    pyProc.stdout.on('data', (data) => { console.log(`PY: ${data}`); });
    pyProc.stderr.on('data', (data) => { console.error(`PYERR: ${data}`); });
}

app.whenReady().then(() => {
    startPython();
    createWindow();
});

app.on('window-all-closed', () => {
    if (pyProc) pyProc.kill();
    if (process.platform !== 'darwin') app.quit();
}); 