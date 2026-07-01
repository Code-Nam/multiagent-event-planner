import os
from pathlib import Path

CLAUDE_DIR: Path = Path(os.environ.get("CLAUDE_DIR", str(Path.home() / ".claude")))
JOBS_DIR: Path = CLAUDE_DIR / "jobs"
PROJECTS_DIR: Path = CLAUDE_DIR / "projects"
