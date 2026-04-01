import subprocess
import sys
import shutil
import platform
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BACKEND_DIR  = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR     = BACKEND_DIR / "venv"

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"


class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"


def log(tag, color, msg):
    print(f"{color}{C.BOLD}[{tag}]{C.RESET} {msg}")


def run(cmd, cwd=None, label=""):
    print(f"\n  {C.CYAN}$ {' '.join(str(c) for c in cmd)}{C.RESET}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        log("ERROR", C.RED, f"Command failed{' (' + label + ')' if label else ''}.")
        sys.exit(result.returncode)


# ✅ Enforce correct Python version
def check_python_version():
    if not ((3, 11) <= sys.version_info < (3, 13)):
        log("ERROR", C.RED,
            f"Use Python 3.11 or 3.12 only. You have {sys.version}")
        sys.exit(1)
    log("OK", C.GREEN, f"Python {sys.version.split()[0]} detected")


def check_node():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        log("OK", C.GREEN, f"Node.js {result.stdout.strip()} detected")
    except FileNotFoundError:
        log("ERROR", C.RED, "Node.js is not installed. https://nodejs.org/")
        sys.exit(1)


def check_npm():
    npm_cmd = "npm.cmd" if IS_WINDOWS else "npm"
    try:
        result = subprocess.run([npm_cmd, "--version"], capture_output=True, text=True)
        log("OK", C.GREEN, f"npm {result.stdout.strip()} detected")
    except FileNotFoundError:
        log("ERROR", C.RED, "npm not found.")
        sys.exit(1)


def remove_venv():
    if VENV_DIR.exists():
        log("CLEAN", C.YELLOW, f"Removing existing venv at {VENV_DIR} ...")
        shutil.rmtree(VENV_DIR)
        log("CLEAN", C.GREEN, "Old venv removed.")
    else:
        log("CLEAN", C.GREEN, "No existing venv found.")


def create_venv():
    log("VENV", C.CYAN, "Creating virtual environment ...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)], label="venv creation")
    log("VENV", C.GREEN, "Virtual environment created.")


# ✅ Improved dependency install
def install_python_deps():
    requirements = BACKEND_DIR / "requirements.txt"

    if not requirements.exists():
        log("ERROR", C.RED, f"requirements.txt not found at {requirements}")
        sys.exit(1)

    log("PIP", C.CYAN, "Upgrading pip, setuptools, wheel ...")
    run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    log("PIP", C.CYAN, "Installing Python dependencies ...")
    run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(requirements)])

    log("PIP", C.GREEN, "Python dependencies installed.")


def install_node_deps():
    npm_cmd = "npm.cmd" if IS_WINDOWS else "npm"
    package_json = FRONTEND_DIR / "package.json"

    if not package_json.exists():
        log("ERROR", C.RED, f"package.json not found at {package_json}")
        sys.exit(1)

    log("NPM", C.CYAN, "Installing frontend npm packages ...")
    run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), label="npm install")
    log("NPM", C.GREEN, "Frontend packages installed.")


def check_env_file():
    env_file = BACKEND_DIR / ".env"

    if not env_file.exists():
        log("WARN", C.YELLOW, ".env file not found. Creating template ...")
        env_file.write_text(
            "# CodeTrace — Environment Variables\n\n"
            "DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/codetrace\n"
            "DB_USER=postgres\n"
            "DB_PASSWORD=YOUR_PASSWORD\n"
            "DB_HOST=localhost\n"
            "DB_PORT=5432\n"
            "DB_NAME=codetrace\n"
        )
        log("WARN", C.YELLOW, "Fill your DB credentials before running.")
    else:
        log("OK", C.GREEN, ".env already exists.")


def main():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════╗
║       CodeTrace — Auto Setup Script      ║
╚══════════════════════════════════════════╝{C.RESET}
""")

    log("STEP 1", C.BOLD, "Checking prerequisites ...")
    check_python_version()
    check_node()
    check_npm()

    print()
    log("STEP 2", C.BOLD, "Setting up Python virtual environment ...")
    remove_venv()
    create_venv()

    print()
    log("STEP 3", C.BOLD, "Installing Python dependencies ...")
    install_python_deps()

    print()
    log("STEP 4", C.BOLD, "Installing frontend dependencies ...")
    install_node_deps()

    print()
    log("STEP 5", C.BOLD, "Checking environment file ...")
    check_env_file()

    print(f"""
{C.GREEN}{C.BOLD}✅ Setup complete!{C.RESET}

{C.BOLD}Important:{C.RESET}
- Use Python 3.11 or 3.12 only
- Make sure PostgreSQL is running

{C.BOLD}Run project:{C.RESET}
  python start_project.py
""")


if __name__ == "__main__":
    main()
