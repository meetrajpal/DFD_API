import os
from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from routers import UserRouter, AuthRouter, MailClickRouter, VideoRouter, DetectRouter, PredictionRouter

load_dotenv(".env")

app = FastAPI(
    title="Deepfake Detection API",
    description="Meet Rajpal",
    docs_url=os.getenv("DOCS"),
    redoc_url=os.getenv("REDOC"),
    openapi_url=os.getenv("OPENAPI"),
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
)

app.include_router(AuthRouter.router)
app.include_router(MailClickRouter.router)
app.include_router(DetectRouter.router)
app.include_router(PredictionRouter.router)
app.include_router(UserRouter.router)
app.include_router(VideoRouter.router)
