import subprocess
import sys
from pathlib import Path

from api.config import SCRIPTS_DIR
from api.models import GenerateResult


def run_script(script_name: str, *args: str) -> GenerateResult:
    path: Path = SCRIPTS_DIR / script_name
    if not path.exists():
        return GenerateResult(ok=False, error=f"Script not found: {script_name}")
    try:
        result = subprocess.run(
            [sys.executable, str(path), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return GenerateResult(ok=False, error="Script timed out after 60 seconds")
    except OSError as exc:
        return GenerateResult(ok=False, error=str(exc))

    if result.returncode == 0:
        return GenerateResult(ok=True, path=result.stdout.strip() or None)
    return GenerateResult(ok=False, error=result.stderr.strip())
