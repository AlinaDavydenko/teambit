from fastapi import FastAPI
from app.api import auth, boards, columns

app = FastAPI()

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(columns.router)


@app.get("/")
def home():
    return {"status": "OK"}
