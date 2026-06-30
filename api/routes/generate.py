from fastapi import APIRouter
from pydantic import BaseModel

from api.models import GenerateResult
from api.services.script_runner import run_script

router = APIRouter()


class GenerateBody(BaseModel):
    input: str | None = None
    output: str | None = None


def _extra_args(body: GenerateBody) -> list[str]:
    args: list[str] = []
    if body.input:
        args += ["--input", body.input]
    if body.output:
        args += ["--output", body.output]
    return args


@router.post("/generate/xlsx", response_model=GenerateResult)
def generate_xlsx(body: GenerateBody = GenerateBody()) -> GenerateResult:
    return run_script("generate-xlsx.py", *_extra_args(body))


@router.post("/generate/docx", response_model=GenerateResult)
def generate_docx(body: GenerateBody = GenerateBody()) -> GenerateResult:
    return run_script("generate-docx.py", *_extra_args(body))


@router.post("/generate/ppt", response_model=GenerateResult)
def generate_ppt(body: GenerateBody = GenerateBody()) -> GenerateResult:
    return run_script("generate-ppt.py", *_extra_args(body))


@router.post("/gmail-draft", response_model=GenerateResult)
def gmail_draft(body: GenerateBody = GenerateBody()) -> GenerateResult:
    return run_script("gmail-draft.py", *_extra_args(body))
