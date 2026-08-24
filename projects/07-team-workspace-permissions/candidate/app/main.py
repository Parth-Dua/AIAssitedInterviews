from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.workspaces import router as workspaces_router

app = FastAPI(title="Team Workspace Permissions Service")
app.include_router(documents_router)
app.include_router(workspaces_router)


@app.get("/health")
def health():
    return {"status": "ok"}
