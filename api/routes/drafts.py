from fastapi import APIRouter

from api.models import Draft, DraftSummary
from api.services.file_store import list_drafts, read_draft

router = APIRouter()


@router.get("/drafts", response_model=list[DraftSummary])
def get_drafts() -> list[DraftSummary]:
    return list_drafts()


@router.get("/drafts/{name}", response_model=Draft)
def get_draft(name: str) -> Draft:
    return read_draft(name)
