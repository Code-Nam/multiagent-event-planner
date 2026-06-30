from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import agents, drafts, event, generate, status

app = FastAPI(
    title="AGEVP API",
    description="HTTP wrapper over the AGEVP multi-agent event planner filesystem and agent runner",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(event.router, prefix="/api")
app.include_router(drafts.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(status.router, prefix="/api")
