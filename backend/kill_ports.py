import subprocess
import sys

# Kill processes on port 8000
pids = [32056, 21856]

for pid in pids:
    try:
        subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, check=False)
        print(f"Killed PID {pid}")
    except Exception as e:
        print(f"Failed to kill PID {pid}: {e}")

print("Done")
