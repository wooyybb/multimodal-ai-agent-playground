from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    user_prompt: str
    provider: str | None = None
    image: str | None = None


class GenerateResponse(BaseModel):
    success: bool
    provider: str | None = None
    score: float | None = None
    image_path: str | None = None
    agent_trace: list[str] = Field(default_factory=list)
    error: str | None = None
