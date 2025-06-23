/**
 * Main process – boots the Electron window.
 * Real menus, IPC wiring, and auto-updates will be added in later milestones.
 */

import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { spawnSync } from 'child_process';

// ─── helper: resolve repo root & python exe ───────────────────────────────
const repoRoot = path.resolve(__dirname, '..', '..');      // LLM_LOADER/
const venvPython = path.join(
  repoRoot,
  '.venv',
  process.platform === 'win32' ? 'Scripts' : 'bin',
  process.platform === 'win32' ? 'python.exe' : 'python'
);
const pythonExe = fs.existsSync(venvPython) ? venvPython : 'python';

console.log('[main] Repo root:', repoRoot);
console.log('[main] Python executable:', pythonExe);

function createWindow() {
  const win = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // DEV: show the Vite dev-server; we'll switch to loadFile() for production
  win.loadURL('http://localhost:5173');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ——— IPC: list-models ———————————————————————————————————————————————
ipcMain.handle("list-models", async () => {
  const result = spawnSync(
    pythonExe,                                            // now correct python
    ["-m", "backend.model_manager.scan_cli", "scan-cache"],
    {
      cwd: repoRoot,                                      // repo root needed
      encoding: "utf-8",
    },
  );

  if (result.status !== 0) {
    console.error("[list-models] CLI error:", result.stderr);
    return [];                    // graceful fallback
  }

  try {
    return JSON.parse(result.stdout || "[]");
  } catch (err) {
    console.error("[list-models] JSON parse error:", err);
    return [];
  }
}); 