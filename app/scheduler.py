import subprocess
import sys
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"
AGENT = BASE_DIR / "app" / "profile_agent.py"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "scheduler.log"


def log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"[{timestamp}] {message}"

    print(line)

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(line + "\n")


def run_agent():
    log("Starting Naukri AI Profile Agent...")

    try:
        result = subprocess.run(
            [
                str(PYTHON),
                str(AGENT),
            ],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=15 * 60,
        )

        if result.stdout:
            with LOG_FILE.open(
                "a",
                encoding="utf-8",
            ) as f:
                f.write(result.stdout)
                f.write("\n")

        if result.stderr:
            with LOG_FILE.open(
                "a",
                encoding="utf-8",
            ) as f:
                f.write(result.stderr)
                f.write("\n")

        if result.returncode == 0:
            log(
                "Naukri AI Profile Agent completed successfully."
            )
        else:
            log(
                "Naukri AI Profile Agent FAILED. "
                f"Exit code: {result.returncode}"
            )

    except subprocess.TimeoutExpired:
        log(
            "Naukri AI Profile Agent timed out "
            "after 15 minutes."
        )

    except Exception as exc:
        log(
            f"Scheduler error: {exc}"
        )


if __name__ == "__main__":
    run_agent()

