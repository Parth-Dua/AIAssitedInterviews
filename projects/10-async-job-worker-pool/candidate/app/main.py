from fastapi import FastAPI

from app.api.routes.batches import router as batches_router

app = FastAPI(title="Async Job Worker Pool")
app.include_router(batches_router)


@app.get("/health")
def health():
    return {"status": "ok"}
