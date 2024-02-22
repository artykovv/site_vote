from fastapi import FastAPI

from user.router import router as user

app = FastAPI(
    title="backend"
)

@app.get("/")
def root():
    return {"data": "hello"}


app.include_router(user)
