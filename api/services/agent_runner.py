import json
from typing import AsyncGenerator

import anthropic

from api.config import AGENTS_DIR, ANTHROPIC_API_KEY

ALLOWED_AGENTS: set[str] = {
    "session-init",
    "venue-scout",
    "info-compiler",
    "budget-validator",
    "event-planner",
    "email-drafter",
    "doc-generator",
    "py-dev",
}

_FALLBACK_MODEL = "claude-haiku-4-5-20251001"


def _load_agent(agent_name: str) -> tuple[str, str]:
    """Return (model, system_prompt) for the named agent."""
    path = AGENTS_DIR / f"{agent_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent file not found: {path}")

    text = path.read_text(encoding="utf-8")

    model = _FALLBACK_MODEL
    system_prompt = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            import yaml  # local import to keep top-level deps minimal

            frontmatter = yaml.safe_load(parts[1]) or {}
            model = str(frontmatter.get("model", _FALLBACK_MODEL))
            # Normalise short aliases (e.g. "haiku") to full model IDs
            if not model.startswith("claude"):
                model = _FALLBACK_MODEL
            system_prompt = parts[2].strip()

    return model, system_prompt


async def stream_agent(
    agent_name: str,
    message: str,
    context: dict | None = None,
) -> AsyncGenerator[str, None]:
    if agent_name not in ALLOWED_AGENTS:
        raise ValueError(f"Agent '{agent_name}' is not in the allowlist")

    try:
        model, system_prompt = _load_agent(agent_name)
    except FileNotFoundError as exc:
        yield f"event: error\ndata: {json.dumps({'message': str(exc), 'code': 'agent_not_found'})}\n\n"
        return

    user_content = message
    if context:
        ctx_block = json.dumps(context, ensure_ascii=False, indent=2)
        user_content = f"<context>\n{ctx_block}\n</context>\n\n{message}"

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    try:
        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            async for text in stream.text_stream:
                payload = json.dumps({"text": text}, ensure_ascii=False)
                yield f"event: chunk\ndata: {payload}\n\n"

        yield f"event: done\ndata: {json.dumps({'agent': agent_name})}\n\n"

    except anthropic.APIStatusError as exc:
        payload = json.dumps({"message": exc.message, "code": str(exc.status_code)})
        yield f"event: error\ndata: {payload}\n\n"
    except anthropic.APIConnectionError as exc:
        payload = json.dumps({"message": str(exc), "code": "connection_error"})
        yield f"event: error\ndata: {payload}\n\n"
