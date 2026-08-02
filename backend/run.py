import sys
import os
import socket
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from backend.config.settings import settings
import uvicorn


def free_port(port: int, host: str = "127.0.0.1"):
    """Kill any process holding the given port."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((host, port))
        s.close()
        if result != 0:
            return  # port is free

        # Find and kill the owning process
        output = subprocess.check_output(
            f'netstat -ano | findstr :{port}',
            shell=True, text=True
        )
        for line in output.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[1].endswith(f":{port}") and "LISTENING" in line:
                pid = parts[-1]
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
    except (subprocess.CalledProcessError, Exception):
        pass


if __name__ == "__main__":
    free_port(settings.SERVER_PORT)

    uvicorn.run(
        "backend.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
