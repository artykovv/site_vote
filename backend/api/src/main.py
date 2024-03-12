from fastapi import FastAPI

from user.router import router as user
from user.router_admin import router as admin_router

app = FastAPI(
    title="backend"
)

app.include_router(admin_router)
app.include_router(user)
