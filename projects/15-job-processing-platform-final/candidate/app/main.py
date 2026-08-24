from fastapi import FastAPI

from app.api.routes.jobs import router as jobs_router

app = FastAPI(title="Job Processing Platform")
app.include_router(jobs_router)


@app.get("/health")
def health():
    return {"status": "ok"}
