import subprocess
import time

for _ in range(3):
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        pids = []
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.append(pid)

        for pid in set(pids):
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], check=False)
                print(f"Killed PID {pid}")
            except:
                pass

        if not pids:
            print("No processes found on port 8000")
            break

        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

print("Done")
