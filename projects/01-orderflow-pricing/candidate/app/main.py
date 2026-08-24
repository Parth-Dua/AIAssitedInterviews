from fastapi import FastAPI

from app.api.routes.orders import router as orders_router

app = FastAPI(title="OrderFlow Pricing Service")
app.include_router(orders_router)


@app.get("/health")
def health():
    return {"status": "ok"}
