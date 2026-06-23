from fastapi import FastAPI
from app.api import auth, boards, columns, cards, websocket, users
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(cards.router)
app.include_router(users.router)
app.include_router(websocket.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return {"status": "OK"}
