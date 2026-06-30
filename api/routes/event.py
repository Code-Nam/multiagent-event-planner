from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.models import EventContext
from api.services.file_store import read_event_context, write_event_context

router = APIRouter()


@router.get("/event", response_model=EventContext)
def get_event() -> EventContext:
    data = read_event_context()
    return EventContext(**data)


@router.post("/event")
def post_event(body: EventContext) -> JSONResponse:
    write_event_context(body.model_dump())
    return JSONResponse({"ok": True})
