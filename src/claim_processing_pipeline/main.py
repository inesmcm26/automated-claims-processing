import uvicorn
from fastapi import FastAPI
from claim_processing_pipeline.api.routers import router
from claim_processing_pipeline.config import Settings, setup_logging

# Set up logging at application startup
settings = Settings.get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Claim Processing API",
    description="API for submitting and managing insurance claims",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("claim_processing_pipeline.main:app", host=settings.API_HOST, port=settings.API_PORT)
