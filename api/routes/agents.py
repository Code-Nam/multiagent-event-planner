from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.models import AgentRunRequest
from api.services.agent_runner import ALLOWED_AGENTS, stream_agent

router = APIRouter()


@router.post("/run/{agent_name}")
async def run_agent(agent_name: str, body: AgentRunRequest) -> StreamingResponse:
    if agent_name not in ALLOWED_AGENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{agent_name}' is not allowed. "
            f"Allowed: {sorted(ALLOWED_AGENTS)}",
        )
    return StreamingResponse(
        stream_agent(agent_name, body.message, body.context),
        media_type="text/event-stream",
    )
