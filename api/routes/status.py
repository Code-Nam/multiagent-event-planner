from fastapi import APIRouter

from api.models import PipelineStatus
from api.services.file_store import pipeline_status

router = APIRouter()


@router.get("/status", response_model=PipelineStatus)
def get_status() -> PipelineStatus:
    return pipeline_status()
