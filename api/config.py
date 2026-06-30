from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]

# api/ lives one level below project root
PROJECT_ROOT: Path = Path(__file__).parent.parent

AGENTS_DIR: Path = PROJECT_ROOT / ".claude" / "agents"
DRAFTS_DIR: Path = PROJECT_ROOT / "drafts"
DOC_CONTENT_DIR: Path = PROJECT_ROOT / "doc-content"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"
EVENT_CONTEXT_PATH: Path = PROJECT_ROOT / "event-context.md"
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"
