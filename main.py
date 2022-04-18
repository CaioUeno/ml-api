from fastapi import FastAPI
from api.v1.api import api_router

app = FastAPI(
    title="ML API", version="0.0.1", description="short description about this API."
)

app.include_router(api_router)


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info", reload=True)
