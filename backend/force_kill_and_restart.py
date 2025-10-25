"""
Force kill all processes on port 8000 and restart backend
"""
import subprocess
import time
import sys

# Step 1: Find and kill all processes on port 8000
print("Finding processes on port 8000...")
result = subprocess.run(
    ['netstat', '-ano'],
    capture_output=True,
    text=True
)

pids = set()
for line in result.stdout.split('\n'):
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                pids.add(int(pid))

print(f"Found PIDs: {pids}")

# Kill each process
for pid in pids:
    print(f"Killing PID {pid}...")
    subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
    time.sleep(0.5)

# Verify they're dead
time.sleep(2)
result = subprocess.run(
    ['netstat', '-ano'],
    capture_output=True,
    text=True
)

still_alive = []
for line in result.stdout.split('\n'):
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                still_alive.append(pid)

if still_alive:
    print(f"WARNING: Some processes still alive: {still_alive}")
else:
    print("All processes killed successfully!")

print("\nPort 8000 is now free. You can start the backend.")
