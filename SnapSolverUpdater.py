import os
import sys
import time
import shutil
import subprocess

def main():
    if len(sys.argv) != 3:
        print("Usage: SnapSolverUpdater.exe <old_exe_path> <new_exe_path>")
        time.sleep(3)
        return

    old_exe = sys.argv[1]
    new_exe = sys.argv[2]

    print("[Updater] Waiting for previous instance to close...")
    time.sleep(2.5)  # Give it a moment to close

    try:
        backup_path = old_exe.replace(".exe", "_backup.exe")

        if os.path.exists(backup_path):
            os.remove(backup_path)

        os.rename(old_exe, backup_path)
        print("[Updater] Backed up old executable to:", backup_path)

        os.rename(new_exe, old_exe)
        print("[Updater] Swapped in new executable.")

        print("[Updater] Launching updated app...")
        subprocess.Popen([old_exe])

    except Exception as e:
        print("[Updater] Error:", e)
        time.sleep(5)

if __name__ == "__main__":
    main()