from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.loans import router as loans_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Library Loan Tracker", lifespan=lifespan)
app.include_router(loans_router)


@app.get("/health")
def health():
    return {"status": "ok"}
