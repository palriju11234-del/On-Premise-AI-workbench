from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sovereign_ai.core.config import APP_NAME, APP_VERSION
from sovereign_ai.core.logger import logger, SovereignException
from sovereign_ai.api.health_router import router as health_router

app = FastAPI(title=APP_NAME, version=APP_VERSION)

@app.exception_handler(SovereignException)
async def sovereign_exception_handler(request: Request, exc: SovereignException):
    logger.error(f"Handled SovereignException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status": "failed"}
    )

app.include_router(health_router)

@app.get("/")
def root():
    return {"message": f"{APP_NAME} Backend is operational."}
