import logging
import logging.config

from fastapi import FastAPI

from api.v1.api import api_router

logging.config.fileConfig("logging.conf")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML API", version="0.0.1", description="short description about this API."
)

app.include_router(api_router, prefix="/api/v1")


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info", reload=True)
