from fastapi import FastAPI

from app.api.routes.tickets import router as tickets_router

app = FastAPI(title="Support Ticket Queue")
app.include_router(tickets_router)


@app.get("/health")
def health():
    return {"status": "ok"}
