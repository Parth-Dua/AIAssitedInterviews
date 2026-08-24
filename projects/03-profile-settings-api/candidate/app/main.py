from fastapi import FastAPI

from app.api.routes.users import router as users_router

app = FastAPI(title="Profile Settings API")
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
