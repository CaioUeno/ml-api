import logging
import logging.config

from fastapi import FastAPI

from api.v1.api import api_router

logging.config.fileConfig("logging.conf")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML API", version="1.0.0", description="Minimal version of twitter to classify/quantify sentiment."
)

app.include_router(api_router, prefix="/api/v1")


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
