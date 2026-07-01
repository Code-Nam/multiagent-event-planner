from pydantic import BaseModel


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    total_tokens: int
    api_call_count: int


class AgentMeta(BaseModel):
    agent_type: str
    description: str
    spawn_depth: int
    usage: TokenUsage | None = None
    model: str | None = None


class Job(BaseModel):
    id: str
    name: str
    template: str
    state: str
    tokens: int
    model: str | None
    cwd: str
    project: str
    created_at: str
    updated_at: str
    source: str = "job"
    usage: TokenUsage | None = None


class JobDetail(Job):
    usage: TokenUsage | None = None
    agents: list[AgentMeta]


class JobList(BaseModel):
    jobs: list[Job]
    total: int


class LiveSnapshot(BaseModel):
    job_id: str
    state: str
    tokens: int
    updated_at: str
    usage: TokenUsage | None = None


class LiveRequest(BaseModel):
    job_id: str
