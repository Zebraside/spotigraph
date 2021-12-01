import subprocess
import sys
import time

processes = []

try:

    processes.append(subprocess.Popen([sys.executable, "saving.py"]))
    processes.append(subprocess.Popen([sys.executable, "scrapping.py"]))
    processes.append(subprocess.Popen([sys.executable, "injection.py"]))
    processes.append(subprocess.Popen([sys.executable, "monitoring.py", "save"]))
    processes.append(subprocess.Popen([sys.executable, "monitoring.py", "artist"]))
    while True:
        time.sleep(1)
finally:
    for process in processes:
        process.kill()

