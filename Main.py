from fastapi import FastAPI
from routers import UserRouter, AuthRouter, MailClickRouter

app = FastAPI(title="Deepfake Detection API", description="Meet Rajpal")

app.include_router(UserRouter.router)
app.include_router(AuthRouter.router)
app.include_router(MailClickRouter.router)


@app.get("/", tags=["Home API"])
async def root_api():
    return {"Hello": "World"}
