from fastapi import FastAPI

from app.api.routes.completions import router as completions_router

app = FastAPI(title="LLM Request Router")
app.include_router(completions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
