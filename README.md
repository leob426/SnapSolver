# SnapSolver

> **By Leo & Mark**

SnapSolver is a handy tool that lets you **quickly capture a screenshot** and **send it to GPT** for an answer. It was made to help people solve stuff in images real quick.

## Features

- **Screenshot Capture**: Press a keybind to open the Windows Snipping Tool, then copy your screenshot.
- **Automatic GPT Answering**: It will send the screenshot to GPT and give back a response right away.
- **Easy Setup**: Just run the app and enter your OpenAI API key once. It remembers it for future use.
- **Self-Updating**: It checks GitHub for a newer version every time you open SnapSolver, so you’re always running the latest version.

## How to Use

1. **Open SnapSolver** by running the .exe file.  
2. If it’s your first time, it will **ask for your OpenAI API key**.  
   - To get one, go to https://platform.openai.com/api-keys and make a key.  
3. Once you enter a valid key, SnapSolver will show “SnapSolver Ready” with the default keybind.  
4. **Press the keybind** (default is `backslash`) to open the Windows Snipping Tool.  
5. Select the area you want to capture, and **copy** it (Snipping Tool usually does that automatically).  
6. Wait a second. SnapSolver talks to GPT and pops up the answer right there in a small window.  
7. That’s all!

### Changing the Keybind

- Click **“Change Keybind”** on the “SnapSolver Ready” window.  
- Type a new key name (like `f12`, `shift+ctrl+k`, etc.) and save it.  
- Next time you press that new key, SnapSolver will do its thing.

## Self-Updating Info

- Every time SnapSolver starts, it checks GitHub to see if there’s a **newer version**.  
- If a new version is found, it automatically downloads the **latest .exe**, replaces the old one, and restarts.  
- You don’t need to do anything! SnapSolver keeps itself current.

## Building from Source

1. **Clone** this repo:  
   ```bash
   git clone https://github.com/<USERNAME>/<REPO>.git
   ```
2. **Install dependencies** in your Python environment:  
   ```bash
   pip install -r requirements.txt
   ```
3. **Build** with PyInstaller (example command):  
   ```bash
   pyinstaller --onefile --icon=SnapSolverIcon.ico SnapSolver.py
   ```
4. After the build is done, you’ll see a `dist` folder containing `SnapSolver.exe`.  
   That’s your app.

## Credits
- **Created by**: Leo & Mark  
- **Logo and Graphics**: Logos Created by Leo & Mark
- **Uses**: PyInstaller, PyAutoGUI, Python’s `requests`, and more.
