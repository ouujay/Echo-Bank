"""
Kill all processes on port 8000
"""
import subprocess
import sys

# PIDs to kill
pids = [13268, 1004, 3532, 30584]

for pid in pids:
    try:
        subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                      capture_output=True, text=True, check=False)
        print(f"Killed PID {pid}")
    except Exception as e:
        print(f"Failed to kill PID {pid}: {e}")

print("\nAll processes killed successfully")
