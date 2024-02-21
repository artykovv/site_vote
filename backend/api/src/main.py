from fastapi import FastAPI

from user.router import router as user

app = FastAPI(
    title="backend"
)

app.include_router(user)
