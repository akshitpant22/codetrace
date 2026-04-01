import subprocess
import sys
import os
import time
import signal
import platform
import webbrowser
import socket
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    VENV_PYTHON  = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    VENV_UVICORN = BACKEND_DIR / "venv" / "Scripts" / "uvicorn.exe"
else:
    VENV_PYTHON  = BACKEND_DIR / "venv" / "bin" / "python"
    VENV_UVICORN = BACKEND_DIR / "venv" / "bin" / "uvicorn"


class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"


def banner():
    print(f"""
{C.CYAN}{C.BOLD}
  ██████╗ ██████╗ ██████╗ ███████╗████████╗██████╗  █████╗  ██████╗███████╗
 ██╔════╝██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
 ██║     ██║   ██║██║  ██║█████╗     ██║   ██████╔╝███████║██║     █████╗
 ██║     ██║   ██║██║  ██║██╔══╝     ██║   ██╔══██╗██╔══██║██║     ██╔══╝
 ╚██████╗╚██████╔╝██████╔╝███████╗   ██║   ██║  ██║██║  ██║╚██████╗███████╗
  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝
{C.RESET}
{C.BOLD}  Code Plagiarism & Duplication Detection System{C.RESET}
""")


def log(prefix: str, color: str, message: str):
    print(f"{color}{C.BOLD}[{prefix}]{C.RESET} {message}")


def check_prerequisites():
    errors = []

    if not VENV_PYTHON.exists():
        errors.append(
            f"Virtual environment not found at {VENV_PYTHON}\n"
            f"  → Run: cd backend && python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt"
        )

    if not VENV_UVICORN.exists():
        errors.append(
            f"uvicorn not found inside venv.\n"
            f"  → Run: cd backend && venv\\Scripts\\activate && pip install -r requirements.txt"
        )

    if not (FRONTEND_DIR / "node_modules").exists():
        errors.append(
            f"Frontend node_modules missing.\n"
            f"  → Run: cd frontend && npm install"
        )

    if errors:
        log("ERROR", C.RED, "Prerequisites check failed:\n")
        for i, err in enumerate(errors, 1):
            print(f"  {C.RED}{i}.{C.RESET} {err}\n")
        sys.exit(1)

    log("CHECK", C.GREEN, "All prerequisites satisfied ✓")


def start_backend() -> subprocess.Popen:
    log("BACKEND", C.BLUE, "Starting FastAPI server on http://localhost:8000 ...")

    cmd = [
        str(VENV_UVICORN),
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
    ]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    return subprocess.Popen(
        cmd,
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
    )


def start_frontend() -> subprocess.Popen:
    log("FRONTEND", C.CYAN, "Starting Vite dev server on http://localhost:5173 ...")

    npm_cmd = "npm.cmd" if IS_WINDOWS else "npm"

    return subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=sys.stdout,
        stderr=sys.stderr
    )


# 🔥 NEW: Wait until port is active
def wait_for_port(port, host="localhost", timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except:
            time.sleep(0.5)
    return False


def main():
    banner()

    log("START", C.GREEN, "Launching CodeTrace development environment...")
    print()

    check_prerequisites()
    print()

    backend_proc  = start_backend()
    time.sleep(1)
    frontend_proc = start_frontend()

    # 🔥 NEW: Auto open browser when frontend is ready
    if wait_for_port(5173):
        log("BROWSER", C.GREEN, "Opening frontend in browser...")
        webbrowser.open("http://localhost:5173")
    else:
        log("WARNING", C.YELLOW, "Frontend not ready, could not open browser automatically.")

    print()
    log("READY", C.GREEN, f"{C.BOLD}Both servers are running!{C.RESET}")
    print(f"""
  {C.CYAN}Frontend  →  {C.BOLD}http://localhost:5173{C.RESET}
  {C.BLUE}Backend   →  {C.BOLD}http://localhost:8000{C.RESET}
  {C.YELLOW}API Docs  →  {C.BOLD}http://localhost:8000/docs{C.RESET}

  {C.YELLOW}Press Ctrl+C to stop all servers.{C.RESET}
""")

    processes = [backend_proc, frontend_proc]

    def shutdown(sig=None, frame=None):
        print()
        log("STOP", C.YELLOW, "Shutting down all servers...")
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        time.sleep(1)
        for proc in processes:
            if proc.poll() is None:
                proc.kill()
        log("STOP", C.GREEN, "All servers stopped. Goodbye! 👋")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    while True:
        for proc in processes:
            ret = proc.poll()
            if ret is not None:
                name = "Backend" if proc is backend_proc else "Frontend"
                log("ERROR", C.RED, f"{name} process exited unexpectedly (code {ret}). Stopping all.")
                shutdown()
        time.sleep(2)


if __name__ == "__main__":
    main()