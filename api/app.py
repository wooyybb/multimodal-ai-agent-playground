from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="Multimodal AI Agent API",
    description="FastAPI service layer for the multi-agent image generation framework.",
    version="0.1.0",
)

app.include_router(router)
