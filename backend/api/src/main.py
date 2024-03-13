from fastapi import FastAPI
from auth.admin.router import router as router_admin
from auth.user.router import router as router_user

app = FastAPI(
    title="backend"
)

app.include_router(router_admin)
app.include_router(router_user)
