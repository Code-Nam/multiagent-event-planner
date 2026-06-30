FROM python:3.12-slim

WORKDIR /app

COPY api/requirements.txt api/requirements.txt
COPY scripts/requirements.txt scripts/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt -r scripts/requirements.txt

COPY api/ api/
COPY scripts/ scripts/
COPY .claude/agents/ .claude/agents/
COPY event-context.md event-context.md

RUN mkdir -p drafts doc-content output

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
