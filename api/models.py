from pydantic import BaseModel


class EventContext(BaseModel):
    name: str
    date: str
    type: str
    expected_attendance: str
    fixed_budget: str
    event_lead: str
    preferred_area: str
    constraints: str


class DraftSummary(BaseModel):
    name: str
    purpose: str
    to: str
    subject: str
    status: str


class Draft(DraftSummary):
    body: str


class OutputFile(BaseModel):
    name: str
    type: str
    path: str


class PipelineStatus(BaseModel):
    event_configured: bool
    drafts_count: int
    doc_content_count: int
    output_count: int
    draft_names: list[str]


class GenerateResult(BaseModel):
    ok: bool
    path: str | None = None
    error: str | None = None


class AgentRunRequest(BaseModel):
    message: str
    context: dict | None = None
