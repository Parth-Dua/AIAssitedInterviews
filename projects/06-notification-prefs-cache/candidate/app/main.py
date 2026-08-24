from fastapi import FastAPI

from app.api.routes.notification_prefs import router as notification_prefs_router

app = FastAPI(title="Notification Preferences Service")
app.include_router(notification_prefs_router)


@app.get("/health")
def health():
    return {"status": "ok"}
