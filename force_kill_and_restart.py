"""
Force kill all Python processes and restart backend cleanly
"""
import subprocess
import time
import sys

print("=" * 60)
print("FORCE KILLING ALL PYTHON PROCESSES")
print("=" * 60)

# Get all python.exe processes
result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                       capture_output=True, text=True)

# Kill each one
subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)

print("\nAll Python processes killed")
print("Waiting 3 seconds...")
time.sleep(3)

# Verify port 8000 is clear
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
port_8000 = [line for line in result.stdout.split('\n') if ':8000' in line and 'LISTENING' in line]

if port_8000:
    print("\nWARNING: Port 8000 still in use!")
    for line in port_8000:
        print(line)
else:
    print("\nPort 8000 is clear!")

print("\n" + "=" * 60)
print("Now manually start backend with:")
print("cd backend && python -m uvicorn app.main:app --reload --port 8000")
print("=" * 60)
