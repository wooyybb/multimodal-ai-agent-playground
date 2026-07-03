from fastapi import APIRouter

from api.schema import GenerateRequest, GenerateResponse
from api.service import run_generation


router = APIRouter()


@router.get("/")
def root():
    return {
        "status": "ok",
        "service": "Multimodal AI Agent FastAPI Service",
    }


@router.get("/health")
def health():
    return {
        "status": "healthy",
    }


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    print("[FastAPI] Request received")
    try:
        return run_generation(
            user_prompt=request.user_prompt,
            provider=request.provider,
            image=request.image,
        )
    except Exception as error:
        print(f"[FastAPI] Generation failed: {error}")
        return GenerateResponse(
            success=False,
            provider=request.provider,
            score=None,
            image_path=None,
            agent_trace=[],
            error=str(error),
        )
