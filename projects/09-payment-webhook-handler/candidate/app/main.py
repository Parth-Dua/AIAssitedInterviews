from fastapi import FastAPI

from app.api.routes.payments import router as payments_router

app = FastAPI(title="Payment Webhook Handler")
app.include_router(payments_router)


@app.get("/health")
def health():
    return {"status": "ok"}
