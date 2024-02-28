from fastapi import FastAPI

from user.router import router as user
from vote.router import router as vote

app = FastAPI(
    title="backend"
)

app.include_router(user)
app.include_router(vote)
