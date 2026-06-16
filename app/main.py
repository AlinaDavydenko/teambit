from fastapi import FastAPI
from app.api import auth, boards, columns, cards
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(cards.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return {"status": "OK"}
