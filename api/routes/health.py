from fastapi import APIRouter

import api.config as cfg

router = APIRouter()


@router.get("/health")
def get_health() -> dict:
    return {"ok": cfg.CLAUDE_DIR.is_dir()}
