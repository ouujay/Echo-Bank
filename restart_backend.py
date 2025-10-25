"""
Force restart backend - Kill ALL processes on port 8000 and start fresh
"""
import subprocess
import time
import sys

def kill_port_8000():
    """Kill all processes listening on port 8000"""
    print("Step 1: Finding processes on port 8000...")
    for attempt in range(5):
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        pids = set()
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)

        if not pids:
            print("✓ No processes found on port 8000")
            return True

        print(f"  Found {len(pids)} processes: {', '.join(pids)}")
        for pid in pids:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid],
                             capture_output=True, check=False)
                print(f"  Killed PID {pid}")
            except:
                pass

        time.sleep(1)

    print("✗ Could not kill all processes")
    return False

def verify_port_clear():
    """Verify port 8000 is completely clear"""
    print("\nStep 2: Verifying port 8000 is clear...")
    time.sleep(2)
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if ':8000' in line and 'LISTENING' in line:
            print("✗ Port 8000 still in use!")
            return False
    print("✓ Port 8000 is clear")
    return True

def start_backend():
    """Start the backend server"""
    print("\nStep 3: Starting backend...")
    print("  Command: cd backend && ../venv/Scripts/uvicorn app.main:app --reload --port 8000")
    print("\n✓ You need to run this manually in a separate terminal")
    print("  OR let Claude Code start it in background")
    return True

if __name__ == "__main__":
    print("="*60)
    print(" BACKEND RESTART SCRIPT")
    print("="*60)

    if not kill_port_8000():
        sys.exit(1)

    if not verify_port_clear():
        sys.exit(1)

    start_backend()

    print("\n" + "="*60)
    print(" DONE - Backend is ready to start")
    print("="*60)
