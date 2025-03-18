import os

from fastapi import FastAPI
from dotenv import load_dotenv
from routers import UserRouter, AuthRouter, MailClickRouter, VideoRouter, FrameRouter
load_dotenv(".env")


app = FastAPI(title="Deepfake Detection API", description="Meet Rajpal", docs_url=os.getenv("DOCS"), redoc_url=os.getenv("REDOC"), openapi_url=os.getenv("OPENAPI"))

app.include_router(AuthRouter.router)
app.include_router(MailClickRouter.router)
app.include_router(UserRouter.router)
app.include_router(VideoRouter.router)
app.include_router(FrameRouter.router)


@app.get("/", tags=["Home"])
async def root_api():
    return {"Hello": "World"}
