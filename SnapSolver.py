import time
import pyautogui
import requests
import keyboard
import subprocess
import os
import sys
import webbrowser
import threading
from PIL import ImageGrab, Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

########################
# (ADDED) Self-update constants/variables
########################
CURRENT_VERSION = "1.0.8"  # Update each time you release
UPDATE_VERSION_URL = "https://raw.githubusercontent.com/leob426/SnapSolver/main/latest_version.txt"
UPDATE_EXE_URL = "https://github.com/leob426/SnapSolver/releases/latest/download/SnapSolver-latest.exe"
EXE_NAME = "SnapSolver.exe"

########################
# 1) Paths for images/icons (PyInstaller logic)
########################
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(BASE_DIR, "SnapSolverLogo.png")
ICON_PATH = os.path.join(BASE_DIR, "SnapSolverIcon.ico")

########################
# 2) A function to get the user's SnapSolver data folder
########################
def get_data_dir():
    if sys.platform.startswith("win"):
        base_folder = os.getenv("APPDATA", os.path.expanduser("~"))
        folder = os.path.join(base_folder, "SnapSolver")
    elif sys.platform.startswith("darwin"):
        base_folder = os.path.expanduser("~/Library/Application Support")
        folder = os.path.join(base_folder, "SnapSolver")
    else:
        base_folder = os.path.expanduser("~/.config")
        folder = os.path.join(base_folder, "SnapSolver")

    os.makedirs(folder, exist_ok=True)
    return folder

########################
# (ADDED) Check for self-updates from GitHub
########################
def check_for_updates():
    """
    A simple example of a self-update check. This will:
      1) Compare CURRENT_VERSION to what's in the GitHub latest_version.txt.
      2) If a new version is found, it downloads the new .exe into the same folder.
      3) Replaces the current executable, and restarts.
    """
    try:
        r = requests.get(UPDATE_VERSION_URL, timeout=5)
        if r.status_code != 200:
            return
        latest_version = r.text.strip()

        if latest_version != CURRENT_VERSION:
            download_update()
    except:
        pass

def download_update():
    """
    Download the new EXE from GitHub, replace the current one, and restart.
    This leaves only one SnapSolver.exe on disk.
    """
    try:
        r = requests.get(UPDATE_EXE_URL, timeout=10, stream=True)
        if r.status_code == 200:
            new_file_path = os.path.join(os.path.dirname(sys.executable), "SnapSolver_new.exe")
            with open(new_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            current_exe_path = os.path.join(os.path.dirname(sys.executable), EXE_NAME)
            backup_old = current_exe_path + ".old"

            try:
                if os.path.exists(backup_old):
                    os.remove(backup_old)
                os.rename(current_exe_path, backup_old)
            except:
                pass

            os.rename(new_file_path, current_exe_path)

            # Remove .old so only one EXE remains
            try:
                os.remove(backup_old)
            except:
                pass

            subprocess.Popen([current_exe_path])
            sys.exit(0)
    except:
        pass

########################
# (NEW) Interactive "Check for Update" function
########################
def check_for_updates_interactive(root):
    """
    Lets the user manually check for an update via a button.
    Shows a popup if there's no update, or downloads if there's a new version.
    """
    try:
        r = requests.get(UPDATE_VERSION_URL, timeout=5)
        if r.status_code != 200:
            messagebox.showinfo("SnapSolver Update", "Failed to check for updates. (Bad response)")
            return

        latest_version = r.text.strip()
        if latest_version != CURRENT_VERSION:
            messagebox.showinfo("SnapSolver Update", f"Downloading new version {latest_version} now...")
            download_update()  # Reuses the same logic as auto-update
        else:
            messagebox.showinfo("SnapSolver Update", "You're already on the latest version.")
    except:
        messagebox.showinfo("SnapSolver Update", "Failed to check for updates. Please try again later.")

########################
# NEW FUNCTION:
# Kill any old SnapSolver instance so only the newest remains
########################
def single_instance_kill_others():
    """
    Checks if there's a SnapSolver.lock file in the data folder,
    which stores an old PID. If found, kills that process.
    Then writes our own PID. If user runs SnapSolver multiple times,
    each new instance kills the old one and takes over.
    """
    data_dir = get_data_dir()
    lock_path = os.path.join(data_dir, 'SnapSolver.lock')
    my_pid = os.getpid()

    if os.path.exists(lock_path):
        with open(lock_path, 'r', encoding='utf-8') as f:
            old_pid_str = f.read().strip()
        if old_pid_str.isdigit():
            old_pid = int(old_pid_str)
            if old_pid != my_pid:
                if sys.platform.startswith('win'):
                    cmd = f"taskkill /PID {old_pid} /F"
                    try:
                        subprocess.run(cmd, shell=True, timeout=3)
                    except:
                        pass
                else:
                    try:
                        os.kill(old_pid, 9)
                    except:
                        pass

    with open(lock_path, 'w', encoding='utf-8') as f:
        f.write(str(my_pid))

########################
# 3) Existing logic for loading/saving the API key
########################
def load_api_key():
    data_dir = get_data_dir()
    path = os.path.join(data_dir, 'api_key.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    return None

def save_api_key(key):
    if validate_api_key(key):
        data_dir = get_data_dir()
        path = os.path.join(data_dir, 'api_key.txt')
        with open(path, 'w', encoding='utf-8') as file:
            file.write(key)
        return True
    return False

def validate_api_key(api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=5)
        return (response.status_code == 200)
    except:
        return False

########################
# 4) Existing logic for loading/saving the keybind
########################
def load_keybind():
    data_dir = get_data_dir()
    path = os.path.join(data_dir, 'keybind.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            kb = f.read().strip()
            if kb:
                return kb
    return 'backslash'

def save_keybind(new_kb):
    data_dir = get_data_dir()
    path = os.path.join(data_dir, 'keybind.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_kb)

########################
# 5) The rest of your SnapSolver code
########################
def load_logo():
    try:
        img = Image.open(LOGO_PATH)
        img = img.resize((140, 140), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

def create_window(root, title):
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("400x340")
    window.configure(bg="#1e1e1e")
    window.resizable(False, False)

    if os.path.exists(ICON_PATH):
        window.iconbitmap(ICON_PATH)

    logo = load_logo()
    if logo:
        logo_label = tk.Label(window, image=logo, bg="#1e1e1e")
        logo_label.image = logo
        logo_label.pack(pady=5)

    tk.Label(
        window,
        text="test",
        fg="white",
        bg="#1e1e1e",
        font=("Segoe UI", 8, "italic")
    ).pack(pady=(0,10))

    return window, logo

def show_message(title, message, root):
    popup, _ = create_window(root, title)

    tk.Label(
        popup,
        text=title,
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=5)

    tk.Label(
        popup,
        text=message,
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 11),
        wraplength=340
    ).pack(pady=5)

    tk.Button(
        popup,
        text="OK",
        command=popup.destroy,
        font=("Segoe UI", 10, "bold"),
        bg="#4CAF50", fg="white",
        relief="flat"
    ).pack(pady=15)

    popup.grab_set()
    popup.wait_window()

def get_api_key(root):
    api_key = load_api_key()
    if api_key and validate_api_key(api_key):
        return api_key

    root.withdraw()
    win, _ = create_window(root, "SnapSolver Key Entry")

    tk.Label(
        win,
        text="Enter OpenAI API Key",
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=5)

    entry = tk.Entry(win, width=40, show='*', font=("Segoe UI", 10), relief="flat")
    entry.pack(pady=8)

    def submit():
        key = entry.get()
        if save_api_key(key):
            win.destroy()
        else:
            messagebox.showerror("Error", "Invalid API Key. Try again.")

    tk.Button(
        win,
        text="Enter API Key",
        command=submit,
        font=("Segoe UI", 10, "bold"),
        bg="#4CAF50", fg="white",
        relief="flat"
    ).pack(pady=5)

    tk.Button(
        win,
        text="Need an API key? Click me!",
        command=lambda: webbrowser.open('https://platform.openai.com/api-keys'),
        font=("Segoe UI", 10), relief="flat"
    ).pack()

    win.wait_window()
    return load_api_key()

def capture_screenshot():
    subprocess.run("powershell Set-Clipboard -Value $null", shell=True)
    time.sleep(0.3)
    pyautogui.hotkey('win', 'shift', 's')

    for _ in range(30):
        screenshot = ImageGrab.grabclipboard()
        if screenshot:
            return screenshot
        time.sleep(0.5)
    return None

def image_to_base64(image):
    from io import BytesIO
    import base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def ask_chatgpt_with_image(image, api_key):
    base64_image = image_to_base64(image)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Answer clearly from image."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Provide only the correct answer clearly formatted if long."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ],
            },
        ],
        "max_tokens": 500
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers, timeout=30)
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

def show_answer_window(answer, root):
    window, _ = create_window(root, "SnapSolver Result")

    content_frame = tk.Frame(window, bg="#1e1e1e")
    content_frame.pack(fill="both", expand=True)

    content_frame.rowconfigure(1, weight=1)
    content_frame.columnconfigure(0, weight=1)

    tk.Label(
        content_frame,
        text="The Answers below are accurate:",
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    ).grid(row=0, column=0, pady=(0,5), padx=10, sticky="w")

    scrolled_box = ScrolledText(
        content_frame,
        wrap="word",
        font=("Segoe UI", 12),
        fg="white",
        bg="#1e1e1e",
        relief="flat"
    )
    scrolled_box.grid(row=1, column=0, sticky="nsew", padx=10)
    scrolled_box.insert("1.0", answer)
    scrolled_box.config(state="disabled")

    ok_button = tk.Button(
        content_frame,
        text="OK",
        command=window.destroy,
        font=("Segoe UI", 10, "bold"),
        bg="#4CAF50", fg="white",
        relief="flat"
    )
    ok_button.grid(row=2, column=0, pady=10)

    window.grab_set()
    window.wait_window()

def show_ready_window(root, keybind):
    """
    Show the "SnapSolver Ready" window with the user’s current keybind,
    plus an option to change it. (Contains credits label from create_window.)
    """
    popup, _ = create_window(root, "SnapSolver Ready")

    tk.Label(
        popup,
        text="SnapSolver Ready",
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=5)

    message = f"✅ Press '{keybind}' to capture screenshots."
    tk.Label(
        popup,
        text=message,
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 11),
        wraplength=340
    ).pack(pady=5)

    btn_frame = tk.Frame(popup, bg="#1e1e1e")
    btn_frame.pack(pady=15)

    # OK button
    tk.Button(
        btn_frame,
        text="OK",
        command=popup.destroy,
        font=("Segoe UI", 10, "bold"),
        bg="#4CAF50", fg="white",
        relief="flat",
        width=12
    ).pack(side="left", padx=5)

    # Change Keybind button
    tk.Button(
        btn_frame,
        text="Change Keybind",
        command=lambda: change_keybind_window(root, popup),
        font=("Segoe UI", 10, "bold"),
        bg="#2196F3", fg="white",
        relief="flat",
        width=12
    ).pack(side="left", padx=5)

    # (NEW) Check for Update button
    tk.Button(
        btn_frame,
        text="Check for Update",
        command=lambda: check_for_updates_interactive(root),
        font=("Segoe UI", 10, "bold"),
        bg="#FFC107", fg="white",
        relief="flat",
        width=14
    ).pack(side="left", padx=5)

    popup.grab_set()
    popup.wait_window()

def change_keybind_window(root, parent_window):
    parent_window.withdraw()
    kb_win, _ = create_window(root, "Change Keybind")

    tk.Label(
        kb_win,
        text="Enter New Keybind:",
        fg="white", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=5)

    entry = tk.Entry(kb_win, width=25, font=("Segoe UI", 10), relief="flat")
    entry.pack(pady=8)

    def save_new_keybind():
        new_kb = entry.get().strip()
        if not new_kb:
            messagebox.showerror("Error", "Keybind cannot be empty.")
            return
        save_keybind(new_kb)
        kb_win.destroy()

    tk.Button(
        kb_win,
        text="Save Keybind",
        command=save_new_keybind,
        font=("Segoe UI", 10, "bold"),
        bg="#4CAF50", fg="white",
        relief="flat"
    ).pack(pady=5)

    kb_win.grab_set()
    kb_win.wait_window()
    parent_window.deiconify()

def main_loop(root):
    api_key = get_api_key(root)
    if not api_key:
        print("Exiting due to invalid API key.")
        return

    user_keybind = load_keybind()
    show_ready_window(root, user_keybind)

    while True:
        user_keybind = load_keybind()
        keyboard.wait(user_keybind)
        screenshot = capture_screenshot()
        if screenshot:
            result = ask_chatgpt_with_image(screenshot, api_key)
            root.after(0, show_answer_window, result, root)
        time.sleep(1)

if __name__ == "__main__":
    # Automatic check for updates at launch
    check_for_updates()

    single_instance_kill_others()

    root = tk.Tk()
    root.withdraw()

    if os.path.exists(ICON_PATH):
        root.iconbitmap(ICON_PATH)

    threading.Thread(target=main_loop, args=(root,), daemon=True).start()
    root.mainloop()




