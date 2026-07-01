from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from api.models import JobDetail, JobList, LiveRequest
from api.services.token_reader import get_job_detail, list_jobs, stream_live_job, ws_live_job

router = APIRouter()

_TRAVERSAL = frozenset({".", ".."})


def _bad_job_id(job_id: str) -> bool:
    return "/" in job_id or job_id in _TRAVERSAL or ".." in job_id.split("/")


@router.get("/jobs", response_model=JobList)
def get_jobs(
    limit: int = Query(default=50, ge=1, le=200), project: str | None = None
) -> JobList:
    return list_jobs(limit=limit, project=project)


@router.post("/jobs/live")
async def live_job(body: LiveRequest) -> StreamingResponse:
    if _bad_job_id(body.job_id):
        raise HTTPException(status_code=400, detail="invalid job id")
    if not get_job_detail(body.job_id):
        raise HTTPException(status_code=404, detail="job not found")
    return StreamingResponse(
        stream_live_job(body.job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(job_id: str) -> JobDetail:
    if _bad_job_id(job_id):
        raise HTTPException(status_code=400, detail="invalid job id")
    detail = get_job_detail(job_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="job not found")
    return detail


@router.websocket("/jobs/{job_id}/ws")
async def live_ws(job_id: str, ws: WebSocket) -> None:
    if _bad_job_id(job_id):
        return  # reject without HTTP 101 upgrade
    await ws.accept()
    if not get_job_detail(job_id):
        await ws.close(code=4004)
        return
    try:
        await ws_live_job(job_id, ws)
    except WebSocketDisconnect:
        pass
