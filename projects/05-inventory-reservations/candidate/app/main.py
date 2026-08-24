from fastapi import FastAPI

from app.api.routes.reservations import router as reservations_router

app = FastAPI(title="Inventory Reservations Service")
app.include_router(reservations_router)


@app.get("/health")
def health():
    return {"status": "ok"}
