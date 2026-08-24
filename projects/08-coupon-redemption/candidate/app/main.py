from fastapi import FastAPI

from app.api.routes.coupons import router as coupons_router

app = FastAPI(title="Coupon Redemption Service")
app.include_router(coupons_router)


@app.get("/health")
def health():
    return {"status": "ok"}
